from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.auto_engine.sqlite.base import Base


class ExecutionPlanRecord(Base):

    __tablename__ = "execution_plans"

    request_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    workflow_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    execute_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    execution_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )
    
    target_object_type: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
        )
    )

    target_account: Mapped[str | None] = (
        mapped_column(
            String,
            nullable=True,
            index=True,
        )
    )