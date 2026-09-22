from sqlalchemy import select

from app.auto_engine.sqlite.access_snapshot import (
    AccessSnapshot,
)
from app.auto_engine.sqlite.db import SessionLocal

class AccessSnapshotRepository:

    def save(
        self,
        snapshot: AccessSnapshot,
    ) -> AccessSnapshot:

        with SessionLocal() as session:

            session.add(
                snapshot
            )

            session.commit()

            session.refresh(
                snapshot
            )

            return snapshot

    def get_by_request_id(
        self,
        request_id: str,
    ) -> AccessSnapshot | None:

        with SessionLocal() as session:

            return (
                session.execute(
                    select(
                        AccessSnapshot
                    ).where(
                        AccessSnapshot.request_id
                        == request_id
                    )
                )
                .scalar_one_or_none()
            )

    def get_latest_by_sam_account_name(
        self,
        sam_account_name: str,
    ) -> AccessSnapshot | None:

        with SessionLocal() as session:

            return (
                session.execute(
                    select(
                        AccessSnapshot
                    )
                    .where(
                        AccessSnapshot.sam_account_name
                        == sam_account_name
                    )
                    .order_by(
                        AccessSnapshot.captured_at.desc()
                    )
                )
                .scalars()
                .first()
            )

    def get_latest_by_employee_id(
        self,
        employee_id: str,
    ) -> AccessSnapshot | None:

        with SessionLocal() as session:

            return (
                session.execute(
                    select(
                        AccessSnapshot
                    )
                    .where(
                        AccessSnapshot.employee_id
                        == employee_id
                    )
                    .order_by(
                        AccessSnapshot.captured_at.desc()
                    )
                )
                .scalars()
                .first()
            )