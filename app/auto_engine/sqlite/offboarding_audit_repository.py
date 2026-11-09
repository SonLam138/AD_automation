import json
from datetime import datetime

from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import IntegrityError

from app.auto_engine.sqlite.db import SessionLocal, engine
from app.auto_engine.sqlite.offboarding_audit_record import (
    OffboardingAuditRecord,
)
from app.auto_engine.sqlite.mail_request_audit_record import (
    HRRequestAuditRecord,
)
from app.auto_engine.sqlite.mail_request_audit_repository import (
    HRRequestAuditRepository,
)


class OffboardingAuditRepository:
    def ensure_schema(self) -> None:
        OffboardingAuditRecord.__table__.create(
            bind=engine,
            checkfirst=True,
        )

        with engine.begin() as connection:
            columns = {
                column["name"]
                for column in inspect(connection).get_columns(
                    OffboardingAuditRecord.__tablename__
                )
            }
            if "response_json" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE offboarding_request_audits "
                        "ADD COLUMN response_json TEXT"
                    )
                )
            if "response_status" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE offboarding_request_audits "
                        "ADD COLUMN response_status INTEGER"
                    )
                )

            indexes = inspect(connection).get_indexes(
                OffboardingAuditRecord.__tablename__
            )
            has_unique_request_id = any(
                index["name"]
                == "uq_offboarding_request_audits_source_request_id"
                and index["unique"]
                and index["column_names"] == ["source_request_id"]
                for index in indexes
            )
            if not has_unique_request_id:
                duplicate_ids = connection.execute(
                    text(
                        "SELECT source_request_id, COUNT(*) "
                        "FROM offboarding_request_audits "
                        "GROUP BY source_request_id HAVING COUNT(*) > 1"
                    )
                ).all()
                if duplicate_ids:
                    duplicate_list = ", ".join(
                        f"{request_id} ({count})"
                        for request_id, count in duplicate_ids
                    )
                    raise RuntimeError(
                        "Cannot enable offboarding idempotency because "
                        "duplicate source_request_id values exist: "
                        f"{duplicate_list}"
                    )

                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS "
                        "uq_offboarding_request_audits_source_request_id "
                        "ON offboarding_request_audits (source_request_id)"
                    )
                )

    def claim(
        self,
        source_request_id: str,
        employee_id: str,
        requested_account: str,
    ) -> tuple[OffboardingAuditRecord, bool]:
        self.ensure_schema()
        now = datetime.utcnow()

        with SessionLocal() as session:
            record = OffboardingAuditRecord(
                source_request_id=source_request_id,
                employee_id=employee_id,
                requested_account=requested_account,
                status="IN_PROGRESS",
                step_outcomes_json="[]",
                started_at=now,
                updated_at=now,
            )
            session.add(record)
            try:
                session.commit()
                session.refresh(record)
                return record, True
            except IntegrityError:
                session.rollback()
                existing = session.execute(
                    select(OffboardingAuditRecord).where(
                        OffboardingAuditRecord.source_request_id
                        == source_request_id
                    )
                ).scalar_one_or_none()
                if existing is None:
                    raise
                return existing, False

    def start(
        self,
        source_request_id: str,
        employee_id: str,
        requested_account: str,
    ) -> int:
        record, created = self.claim(
            source_request_id=source_request_id,
            employee_id=employee_id,
            requested_account=requested_account,
        )
        if not created:
            raise ValueError(
                "An offboarding audit already exists for this "
                "source_request_id"
            )
        return record.id

    def get_by_source_request_id(
        self,
        source_request_id: str,
    ) -> OffboardingAuditRecord | None:
        self.ensure_schema()
        with SessionLocal() as session:
            return session.execute(
                select(OffboardingAuditRecord).where(
                    OffboardingAuditRecord.source_request_id
                    == source_request_id
                )
            ).scalar_one_or_none()

    def get_plan_responses_by_source_request_ids(
        self,
        source_request_ids: list[str],
    ) -> list[tuple[str, int | None, str | None]]:
        self.ensure_schema()
        request_ids = list(dict.fromkeys(source_request_ids))
        responses = []

        for offset in range(0, len(request_ids), 500):
            batch = request_ids[offset:offset + 500]
            with SessionLocal() as session:
                rows = session.execute(
                    select(
                        OffboardingAuditRecord.source_request_id,
                        OffboardingAuditRecord.response_status,
                        OffboardingAuditRecord.response_json,
                    ).where(
                        OffboardingAuditRecord.source_request_id.in_(batch)
                    )
                ).all()
                responses.extend(rows)

        return [
            (source_request_id, response_status, response_json)
            for source_request_id, response_status, response_json in responses
        ]

    def complete(
        self,
        audit_id: int,
        status: str,
        response: dict,
        response_status: int,
        actual_account: str | None = None,
    ) -> None:
        if status not in {
            "SCHEDULED",
            "SUCCESS",
            "FAILED",
            "DRY_RUN",
        }:
            raise ValueError(f"Invalid offboarding audit status: {status}")

        updated_at = datetime.utcnow()
        with SessionLocal() as session:
            record = session.execute(
                select(OffboardingAuditRecord).where(
                    OffboardingAuditRecord.id == audit_id
                )
            ).scalar_one()
            record.status = status
            record.actual_account = actual_account
            record.response_json = json.dumps(
                response,
                default=str,
            )
            record.response_status = response_status
            record.updated_at = updated_at
            record.completed_at = (
                None
                if status == "SCHEDULED"
                else updated_at
            )
            if status == "SCHEDULED":
                HRRequestAuditRecord.__table__.create(
                    bind=engine,
                    checkfirst=True,
                )
                HRRequestAuditRepository.record_plan_acceptance(
                    session,
                    source_request_id=record.source_request_id,
                    employee_id=record.employee_id,
                    request_type="EMPLOYEE_OFFBOARDING",
                    response=response,
                    response_status=response_status,
                    created_at=record.started_at,
                )
            session.commit()

    def record_step(
        self,
        audit_id: int,
        step_name: str,
        success: bool,
        started_at: datetime,
        completed_at: datetime,
        details: dict | None = None,
    ) -> None:
        outcome = {
            "step": step_name,
            "success": success,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_ms": max(
                0,
                int((completed_at - started_at).total_seconds() * 1000),
            ),
        }
        if details:
            outcome["details"] = details

        with SessionLocal() as session:
            record = session.execute(
                select(OffboardingAuditRecord).where(
                    OffboardingAuditRecord.id == audit_id
                )
            ).scalar_one()
            outcomes = json.loads(record.step_outcomes_json)
            existing_index = next(
                (
                    index
                    for index, item in enumerate(outcomes)
                    if item.get("step") == step_name
                ),
                None,
            )
            if existing_index is None:
                outcomes.append(outcome)
            else:
                outcomes[existing_index] = outcome
            record.step_outcomes_json = json.dumps(
                outcomes,
                default=str,
            )
            record.updated_at = datetime.utcnow()
            session.commit()

    def finish(
        self,
        audit_id: int,
        status: str,
        actual_account: str | None = None,
    ) -> None:
        if status not in {"SUCCESS", "FAILED", "DRY_RUN"}:
            raise ValueError(f"Invalid offboarding audit status: {status}")

        completed_at = datetime.utcnow()
        with SessionLocal() as session:
            record = session.execute(
                select(OffboardingAuditRecord).where(
                    OffboardingAuditRecord.id == audit_id
                )
            ).scalar_one()
            record.status = status
            record.actual_account = actual_account
            record.updated_at = completed_at
            record.completed_at = completed_at
            session.commit()

    def count_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        self.ensure_schema()
        with SessionLocal() as session:
            return (
                session.query(
                    func.count(OffboardingAuditRecord.id)
                )
                .filter(
                    OffboardingAuditRecord.started_at >= start_date
                )
                .filter(
                    OffboardingAuditRecord.started_at <= end_date
                )
                .scalar()
                or 0
            )

    def group_by_status(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, int | str]]:
        self.ensure_schema()
        with SessionLocal() as session:
            rows = (
                session.query(
                    OffboardingAuditRecord.status,
                    func.count(OffboardingAuditRecord.id),
                )
                .filter(
                    OffboardingAuditRecord.started_at >= start_date
                )
                .filter(
                    OffboardingAuditRecord.started_at <= end_date
                )
                .group_by(OffboardingAuditRecord.status)
                .all()
            )

            return [
                {"status": status, "total": total}
                for status, total in rows
            ]

    def get_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[OffboardingAuditRecord]:
        self.ensure_schema()
        with SessionLocal() as session:
            return (
                session.query(OffboardingAuditRecord)
                .filter(
                    OffboardingAuditRecord.started_at >= start_date
                )
                .filter(
                    OffboardingAuditRecord.started_at <= end_date
                )
                .order_by(
                    OffboardingAuditRecord.started_at.desc()
                )
                .all()
            )
