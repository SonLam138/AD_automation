from datetime import datetime

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.auto_engine.sqlite.db import SessionLocal, engine
from app.auto_engine.sqlite.mail_request_audit_record import (
    HRRequestAuditRecord,
)


class HRRequestAuditRepository:

    def ensure_schema(self) -> None:
        HRRequestAuditRecord.__table__.create(
            bind=engine,
            checkfirst=True,
        )
        with engine.begin() as connection:
            connection.execute(
                text("DROP TABLE IF EXISTS mail_request_audits")
            )

    def save(
        self,
        record: HRRequestAuditRecord,
    ) -> HRRequestAuditRecord | None:
        if not self.is_mail_source_request_id(record.source_request_id):
            return None

        with SessionLocal() as session:
            existing = session.execute(
                select(HRRequestAuditRecord).where(
                    HRRequestAuditRecord.source_request_id
                    == record.source_request_id
                )
            ).scalar_one_or_none()
            if existing is not None:
                if existing.plan_request_id != record.plan_request_id:
                    raise ValueError(
                        "source_request_id is already associated with "
                        "a different AD plan."
                    )
                return existing

            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_by_request_id(
        self,
        request_id: str,
    ) -> HRRequestAuditRecord | None:
        with SessionLocal() as session:
            by_plan_id = session.execute(
                select(HRRequestAuditRecord).where(
                    HRRequestAuditRecord.plan_request_id
                    == request_id
                )
            ).scalar_one_or_none()
            if by_plan_id is not None:
                return by_plan_id
            return session.get(
                HRRequestAuditRecord,
                request_id,
            )

    def get_by_source_request_id(
        self,
        source_request_id: str,
    ) -> HRRequestAuditRecord | None:
        with SessionLocal() as session:
            return session.get(
                HRRequestAuditRecord,
                source_request_id,
            )

    def get_scheduled_source_request_ids(
        self,
        source_request_ids: list[str],
    ) -> list[str]:
        requested_ids = list(dict.fromkeys(source_request_ids))
        if not requested_ids:
            return []

        scheduled_ids = set()
        for offset in range(0, len(requested_ids), 500):
            batch = requested_ids[offset:offset + 500]
            with SessionLocal() as session:
                scheduled_ids.update(
                    session.execute(
                        select(HRRequestAuditRecord.source_request_id)
                        .where(
                            HRRequestAuditRecord.source_request_id.in_(batch)
                        )
                        .where(
                            HRRequestAuditRecord.request_type.in_(
                                [
                                    "EMPLOYEE_ONBOARDING",
                                    "EMPLOYEE_OFFBOARDING",
                                ]
                            )
                        )
                    )
                    .scalars()
                    .all()
                )

        return sorted(scheduled_ids)

    @staticmethod
    def record_plan_acceptance(
        session: Session,
        *,
        source_request_id: str,
        employee_id: str,
        request_type: str,
        response: dict,
        response_status: int,
        created_at: datetime,
    ) -> None:
        if (
            not HRRequestAuditRepository.is_mail_source_request_id(
                source_request_id
            )
            or not 200 <= response_status < 300
            or response.get("success") is not True
            or not response.get("request_id")
        ):
            return

        plan_request_id = str(response["request_id"])
        existing = session.execute(
            select(HRRequestAuditRecord).where(
                HRRequestAuditRecord.source_request_id
                == source_request_id
            )
        ).scalar_one_or_none()
        if existing is not None:
            if existing.plan_request_id != plan_request_id:
                raise ValueError(
                    "source_request_id is already associated with "
                    "a different AD plan."
                )
            return

        session.add(
            HRRequestAuditRecord(
                source_request_id=source_request_id,
                plan_request_id=plan_request_id,
                workflow_id=str(
                    response.get("workflow_id")
                    or request_type
                ),
                request_type=request_type,
                reason=None,
                employee_id=employee_id,
                email=None,
                source_reference=None,
                sender=None,
                subject=None,
                is_emergency=False,
                created_at=created_at,
            )
        )

    @staticmethod
    def is_mail_source_request_id(
        source_request_id: str | None,
    ) -> bool:
        return bool(
            source_request_id
            and source_request_id.strip().isdecimal()
        )

    def count(self) -> int:
        with SessionLocal() as session:
            return session.query(HRRequestAuditRecord).count()

    def get_latest(
        self,
        limit: int = 20,
    ) -> list[HRRequestAuditRecord]:
        with SessionLocal() as session:
            return (
                session.query(HRRequestAuditRecord)
                .order_by(HRRequestAuditRecord.created_at.desc())
                .limit(limit)
                .all()
            )

    def get_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[HRRequestAuditRecord]:
        with SessionLocal() as session:
            return (
                session.execute(
                    select(HRRequestAuditRecord)
                    .where(HRRequestAuditRecord.created_at >= start_date)
                    .where(HRRequestAuditRecord.created_at <= end_date)
                    .order_by(HRRequestAuditRecord.created_at.desc())
                )
                .scalars()
                .all()
            )

    def count_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        with SessionLocal() as session:
            return session.execute(
                select(func.count())
                .select_from(HRRequestAuditRecord)
                .where(HRRequestAuditRecord.created_at >= start_date)
                .where(HRRequestAuditRecord.created_at <= end_date)
            ).scalar_one()

    def count_emergency_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        with SessionLocal() as session:
            return session.execute(
                select(func.count())
                .select_from(HRRequestAuditRecord)
                .where(HRRequestAuditRecord.is_emergency.is_(True))
                .where(HRRequestAuditRecord.created_at >= start_date)
                .where(HRRequestAuditRecord.created_at <= end_date)
            ).scalar_one()

    def group_by_workflow(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict]:
        with SessionLocal() as session:
            rows = session.execute(
                select(
                    HRRequestAuditRecord.workflow_id,
                    func.count().label("total"),
                )
                .where(HRRequestAuditRecord.created_at >= start_date)
                .where(HRRequestAuditRecord.created_at <= end_date)
                .group_by(HRRequestAuditRecord.workflow_id)
                .order_by(func.count().desc())
            ).all()
            return [
                {"workflow_id": workflow_id, "total": total}
                for workflow_id, total in rows
            ]

    def group_by_reason(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict]:
        with SessionLocal() as session:
            rows = session.execute(
                select(
                    HRRequestAuditRecord.reason,
                    func.count().label("total"),
                )
                .where(HRRequestAuditRecord.created_at >= start_date)
                .where(HRRequestAuditRecord.created_at <= end_date)
                .group_by(HRRequestAuditRecord.reason)
                .order_by(func.count().desc())
            ).all()
            return [
                {"reason": reason, "total": total}
                for reason, total in rows
            ]


MailRequestAuditRepository = HRRequestAuditRepository
