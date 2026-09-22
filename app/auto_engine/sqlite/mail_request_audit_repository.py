from sqlalchemy import func, select

from app.auto_engine.sqlite.db import (
    SessionLocal,
)
from datetime import datetime
from app.auto_engine.sqlite.mail_request_audit_record import (
    MailRequestAuditRecord,
)


class MailRequestAuditRepository:

    def save(
        self,
        record: MailRequestAuditRecord,
    ) -> MailRequestAuditRecord:

        session = SessionLocal()

        try:

            session.add(
                record
            )

            session.commit()

            session.refresh(
                record
            )

            return record

        finally:

            session.close()

    def get_by_request_id(
        self,
        request_id: str,
    ) -> MailRequestAuditRecord | None:

        session = SessionLocal()

        try:

            statement = (
                select(
                    MailRequestAuditRecord
                )
                .where(
                    MailRequestAuditRecord.request_id
                    ==
                    request_id
                )
            )

            return (
                session.execute(
                    statement
                )
                .scalar_one_or_none()
            )

        finally:

            session.close()

    def count(
        self,
    ) -> int:

        session = SessionLocal()

        try:

            return (
                session.query(
                    MailRequestAuditRecord
                )
                .count()
            )

        finally:

            session.close()

    def get_latest(
        self,
        limit: int = 20,
    ) -> list[
        MailRequestAuditRecord
    ]:

        session = SessionLocal()

        try:

            return (
                session.query(
                    MailRequestAuditRecord
                )
                .order_by(
                    MailRequestAuditRecord.created_at.desc()
                )
                .limit(
                    limit
                )
                .all()
            )

        finally:

            session.close()

    def get_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[MailRequestAuditRecord]:

        session = SessionLocal()

        try:

            statement = (
                select(
                    MailRequestAuditRecord
                )
                .where(
                    MailRequestAuditRecord.created_at
                    >=
                    start_date
                )
                .where(
                    MailRequestAuditRecord.created_at
                    <=
                    end_date
                )
                .order_by(
                    MailRequestAuditRecord.created_at.desc()
                )
            )

            return (
                session.execute(
                    statement
            )
            .scalars()
            .all()
        )

        finally:

            session.close()

    def count_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> int:

        session = SessionLocal()

        try:

            statement = (
                select(
                    func.count()
                )
                .select_from(
                    MailRequestAuditRecord
                )
                .where(
                    MailRequestAuditRecord.created_at
                    >=
                    start_date
                )
                .where(
                    MailRequestAuditRecord.created_at
                    <=
                    end_date
                )
            )

            return (
                session.execute(
                    statement
                )
                .scalar_one()
            )

        finally:

            session.close()

    def count_emergency_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> int:

        session = SessionLocal()

        try:

            statement = (
                select(
                    func.count()
                )
                .select_from(
                    MailRequestAuditRecord
                )
                .where(
                    MailRequestAuditRecord.is_emergency
                    ==
                    True
                )
                .where(
                    MailRequestAuditRecord.created_at
                    >=
                    start_date
                )
                .where(
                    MailRequestAuditRecord.created_at
                    <=
                    end_date
                )
            )

            return (
                session.execute(
                    statement
                )
                .scalar_one()
            )

        finally:

            session.close()

    def group_by_workflow(
        self,
        start_date: datetime,
        end_date: datetime,
    ):

        session = SessionLocal()

        try:

            statement = (
                select(
                    MailRequestAuditRecord.workflow_id,

                    func.count().label(
                        "total"
                    )
                )
                .where(
                    MailRequestAuditRecord.created_at
                    >=
                    start_date
                )
                .where(
                    MailRequestAuditRecord.created_at
                    <=
                    end_date
                )
                .group_by(
                    MailRequestAuditRecord.workflow_id
                )
                .order_by(
                    func.count().desc()
                )
            )

            rows = (
                session.execute(
                    statement
                )
                .all()
            )

            return [
                {
                    "workflow_id": row[0],
                    "total": row[1],
                }
                for row in rows
            ]

        finally:

            session.close()

    def group_by_reason(
        self,
        start_date: datetime,
        end_date: datetime,
    ):

        session = SessionLocal()

        try:

            statement = (
                select(
                    MailRequestAuditRecord.reason,

                    func.count().label(
                        "total"
                    )
                )
                .where(
                    MailRequestAuditRecord.created_at
                    >=
                    start_date
                )
                .where(
                    MailRequestAuditRecord.created_at
                    <=
                    end_date
                )
                .group_by(
                    MailRequestAuditRecord.reason
                )
                .order_by(
                    func.count().desc()
                )
            )

            rows = (
                session.execute(
                    statement
                )
                .all()
            )

            return [
                {
                    "reason": row[0],
                    "total": row[1],
                }
                for row in rows
            ]

        finally:

            session.close()
