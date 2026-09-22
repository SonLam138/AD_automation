from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.auto_engine.sqlite.base import (
    Base,
)


class MailRequestAuditRecord(
    Base
):

    __tablename__ = (
        "mail_request_audits"
    )

    request_id: Mapped[str] = (
        mapped_column(
            String,
            primary_key=True,
        )
    )

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

    reason: Mapped[str] = (
        mapped_column(
            String,
            nullable=False,
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

    email: Mapped[str] = (
        mapped_column(
            String,
            nullable=False,
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
            default=datetime.now,
            nullable=False,
            index=True,
        )
    )