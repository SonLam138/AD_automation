from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.auto_engine.sqlite.base import Base


class WorkflowJournalRecord(Base):

    __tablename__ = "workflow_journal"

    journal_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    workflow_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    workflow_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_by: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="saved",
    )

    saved_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    object_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    step_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    snapshot_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )