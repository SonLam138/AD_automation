# app/auto_engine/sqlite/access_snapshot.py

from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
    Text,
    Integer
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.auto_engine.sqlite.base import Base

from datetime import datetime


class AccessSnapshot(
    Base
):

    __tablename__ = (
        "access_snapshots"
    )

    id: Mapped[int] = (
        mapped_column(
            Integer,
            primary_key=True,
            autoincrement=True,
        )
    )

    request_id: Mapped[str] = (
        mapped_column(
            String(128),
            nullable=False,
            index=True,
        )
    )

    request_context: Mapped[str] = (
        mapped_column(
            String(128),
            nullable=False,
        )
    )

    employee_id: Mapped[str] = (
        mapped_column(
            String(128),
            nullable=False,
            index=True,
        )
    )

    sam_account_name: Mapped[str] = (
        mapped_column(
            String(128),
            nullable=False,
            index=True,
        )
    )

    captured_at: Mapped[datetime] = (
        mapped_column(
            DateTime,
            nullable=False,
        )
    )

    snapshot_json: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )