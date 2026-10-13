from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.auto_engine.sqlite.base import Base


class OnboardingAuditRecord(Base):
    __tablename__ = "onboarding_request_audits"
    __table_args__ = (
        Index(
            "uq_onboarding_request_audits_source_request_id",
            "source_request_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    source_request_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    employee_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )
    requested_account: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    actual_account: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    step_outcomes_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    response_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    response_status: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
