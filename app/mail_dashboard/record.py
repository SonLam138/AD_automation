from sqlalchemy import (
    Index,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.auto_engine.sqlite.base import (
    Base,
)


class MailDashboardRecord(Base):
    __tablename__ = "mail_dashboard_snapshots"
    __table_args__ = (
        Index(
            "idx_mail_dashboard_state_changed",
            "processing_state",
            "state_changed_at",
        ),
        Index(
            "idx_mail_dashboard_received_at",
            "received_at",
        ),
    )

    source_system: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    mailbox: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    source_mail_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    subject: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    received_at: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    processing_state: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    state_changed_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    updated_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
