import json
from datetime import datetime

from sqlalchemy import inspect, select, func, text
from sqlalchemy.exc import IntegrityError

from app.auto_engine.sqlite.db import SessionLocal, engine
from app.auto_engine.sqlite.onboarding_audit_record import (
    OnboardingAuditRecord,
)


class OnboardingAuditRepository:
    def ensure_schema(self) -> None:
        OnboardingAuditRecord.__table__.create(
            bind=engine,
            checkfirst=True,
        )

        with engine.begin() as connection:
            columns = {
                column["name"]
                for column in inspect(connection).get_columns(
                    OnboardingAuditRecord.__tablename__
                )
            }
            if "response_json" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE onboarding_request_audits "
                        "ADD COLUMN response_json TEXT"
                    )
                )
            if "response_status" not in columns:
                connection.execute(
                    text(
                        "ALTER TABLE onboarding_request_audits "
                        "ADD COLUMN response_status INTEGER"
                    )
                )

            indexes = inspect(connection).get_indexes(
                OnboardingAuditRecord.__tablename__
            )
            has_unique_request_id = any(
                index["name"]
                == "uq_onboarding_request_audits_source_request_id"
                and index["unique"]
                and index["column_names"] == ["source_request_id"]
                for index in indexes
            )
            if not has_unique_request_id:
                duplicate_ids = connection.execute(
                    text(
                        "SELECT source_request_id, COUNT(*) "
                        "FROM onboarding_request_audits "
                        "GROUP BY source_request_id HAVING COUNT(*) > 1"
                    )
                ).all()
                if duplicate_ids:
                    duplicate_list = ", ".join(
                        f"{request_id} ({count})"
                        for request_id, count in duplicate_ids
                    )
                    raise RuntimeError(
                        "Cannot enable onboarding idempotency because "
                        "duplicate source_request_id values exist: "
                        f"{duplicate_list}"
                    )

                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS "
                        "uq_onboarding_request_audits_source_request_id "
                        "ON onboarding_request_audits (source_request_id)"
                    )
                )

    def claim(
        self,
        source_request_id: str,
        employee_id: str,
        requested_account: str,
    ) -> tuple[OnboardingAuditRecord, bool]:
        self.ensure_schema()
        now = datetime.utcnow()

        with SessionLocal() as session:
            record = OnboardingAuditRecord(
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
                    select(OnboardingAuditRecord).where(
                        OnboardingAuditRecord.source_request_id
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
                "An onboarding audit already exists for this "
                "source_request_id"
            )
        return record.id

    def complete(
        self,
        audit_id: int,
        status: str,
        response: dict,
        response_status: int,
        actual_account: str | None = None,
    ) -> None:
        if status not in {"SUCCESS", "FAILED", "DRY_RUN"}:
            raise ValueError(f"Invalid onboarding audit status: {status}")

        completed_at = datetime.utcnow()
        with SessionLocal() as session:
            record = session.execute(
                select(OnboardingAuditRecord).where(
                    OnboardingAuditRecord.id == audit_id
                )
            ).scalar_one()
            record.status = status
            record.actual_account = actual_account
            record.response_json = json.dumps(response)
            record.response_status = response_status
            record.updated_at = completed_at
            record.completed_at = completed_at
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
                select(OnboardingAuditRecord).where(
                    OnboardingAuditRecord.id == audit_id
                )
            ).scalar_one()
            outcomes = json.loads(record.step_outcomes_json)
            outcomes.append(outcome)
            record.step_outcomes_json = json.dumps(outcomes)
            record.updated_at = datetime.utcnow()
            session.commit()

    def finish(
        self,
        audit_id: int,
        status: str,
        actual_account: str | None = None,
    ) -> None:
        if status not in {"SUCCESS", "FAILED", "DRY_RUN"}:
            raise ValueError(f"Invalid onboarding audit status: {status}")

        completed_at = datetime.utcnow()
        with SessionLocal() as session:
            record = session.execute(
                select(OnboardingAuditRecord).where(
                    OnboardingAuditRecord.id == audit_id
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

        with SessionLocal() as session:

            return (
                session.query(
                    func.count(
                        OnboardingAuditRecord.id
                    )
                )
                .filter(
                    OnboardingAuditRecord.started_at
                    >= start_date
                )
                .filter(
                    OnboardingAuditRecord.started_at
                    <= end_date
                )
                .scalar()
                or 0
            )

    def group_by_status(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, int | str]]:
        with SessionLocal() as session:
            rows = (
                session.query(
                    OnboardingAuditRecord.status,
                    func.count(
                        OnboardingAuditRecord.id
                    )
                )
                .filter(
                    OnboardingAuditRecord.started_at
                    >= start_date
                )
                .filter(
                    OnboardingAuditRecord.started_at
                    <= end_date
                )
                .group_by(
                    OnboardingAuditRecord.status
                )
                .all()
            )

            return [
                {
                    "status": status,
                    "total": total,
                }
                for status, total in rows
            ]

    def get_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[OnboardingAuditRecord]:
        with SessionLocal() as session:
            return (
                session.query(
                    OnboardingAuditRecord
                )
                .filter(
                    OnboardingAuditRecord.started_at
                    >= start_date
                )
                .filter(
                    OnboardingAuditRecord.started_at
                    <= end_date
                )
                .order_by(
                    OnboardingAuditRecord.started_at
                    .desc()
                )
                .all()
            )
