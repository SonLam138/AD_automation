from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    synonym,
)

from app.auto_engine.sqlite.base import (
    Base,
)


class HRRequestAuditRecord(
    Base
):

    __tablename__ = (
        "HR_request_audits"
    )

    source_request_id: Mapped[str] = (
        mapped_column(
            String,
            primary_key=True,
        )
    )

    plan_request_id: Mapped[str] = (
        mapped_column(
            String,
            nullable=False,
            unique=True,
        )
    )

    request_id: Mapped[str] = synonym("plan_request_id")

    workflow_id: Mapped[str] = (
        mapped_column(
            String,
            nullable=False,
            index=True,
        )
    )

    request_type: Mapped[str] = (
        mapped_column(
            String,
            nullable=False,
            index=True,
        )
    )

    reason: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
            index=True,
        )
    )

    employee_id: Mapped[str] = (
        mapped_column(
            String,
            nullable=False,
            index=True,
        )
    )

    email: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
            index=True,
        )
    )

    source_reference: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
        )
    )

    sender: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
            index=True,
        )
    )

    subject: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
        )
    )

    is_emergency: Mapped[bool] = (
        mapped_column(
            Boolean,
            nullable=False,
            default=False,
            index=True,
        )
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            nullable=False,
            index=True,
        )
    )


MailRequestAuditRecord = HRRequestAuditRecord