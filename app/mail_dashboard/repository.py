from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)

from sqlalchemy import (
    and_,
    case,
    func,
    select,
    update,
)
from sqlalchemy.dialects.sqlite import (
    insert as sqlite_insert,
)

from app.auto_engine.sqlite.db import (
    SessionLocal,
    engine,
)
from app.mail_dashboard.record import (
    MailDashboardRecord,
)
from app.mail_dashboard.schemas import (
    MailDashboardSnapshot,
)


FAILED_MAIL_STATES = (
    "RETRY_PENDING",
    "BUSINESS_REJECTED",
    "INVALID_REQUEST",
    "UNSUPPORTED_REQUEST",
    "RETRY_EXHAUSTED",
)


class MailDashboardSnapshotConflict(Exception):
    pass


@dataclass(frozen=True)
class MailDashboardUpsertResult:
    status: str
    changed: bool


class MailDashboardRepository:
    def ensure_schema(self) -> None:
        MailDashboardRecord.__table__.create(
            bind=engine,
            checkfirst=True,
        )

    def upsert(
        self,
        snapshot: MailDashboardSnapshot,
    ) -> MailDashboardUpsertResult:
        self.ensure_schema()
        values = snapshot.to_record_values()
        now = datetime.now(timezone.utc).isoformat(
            timespec="microseconds",
        )
        insert_values = {
            **values,
            "created_at": now,
            "updated_at": now,
        }

        with SessionLocal() as session:
            insert_statement = (
                sqlite_insert(MailDashboardRecord)
                .values(**insert_values)
                .on_conflict_do_nothing(
                    index_elements=[
                        MailDashboardRecord.source_system,
                        MailDashboardRecord.mailbox,
                        MailDashboardRecord.source_mail_id,
                    ],
                )
            )
            insert_result = session.execute(insert_statement)
            if insert_result.rowcount:
                session.commit()
                return MailDashboardUpsertResult(
                    status="created",
                    changed=True,
                )

            existing = session.execute(
                select(MailDashboardRecord).where(
                    MailDashboardRecord.source_system
                    == snapshot.source_system,
                    MailDashboardRecord.mailbox
                    == snapshot.mailbox,
                    MailDashboardRecord.source_mail_id
                    == snapshot.source_mail_id,
                )
            ).scalar_one()

            existing_timestamp = datetime.fromisoformat(
                existing.state_changed_at
            )
            incoming_timestamp = snapshot.state_changed_at
            if incoming_timestamp < existing_timestamp:
                session.rollback()
                return MailDashboardUpsertResult(
                    status="stale",
                    changed=False,
                )

            if (
                incoming_timestamp == existing_timestamp
                and snapshot.processing_state != existing.processing_state
            ):
                session.rollback()
                raise MailDashboardSnapshotConflict(
                    "Different processing states have the same "
                    "state_changed_at timestamp"
                )
            if (
                incoming_timestamp > existing_timestamp
                and snapshot.processing_state == existing.processing_state
            ):
                session.rollback()
                raise MailDashboardSnapshotConflict(
                    "state_changed_at may only advance when "
                    "processing_state changes"
                )

            is_unchanged = all(
                getattr(existing, field_name) == value
                for field_name, value in values.items()
                if field_name not in {
                    "source_system",
                    "mailbox",
                    "source_mail_id",
                }
            )
            if is_unchanged:
                session.rollback()
                return MailDashboardUpsertResult(
                    status="unchanged",
                    changed=False,
                )

            update_statement = (
                update(MailDashboardRecord)
                .where(
                    MailDashboardRecord.source_system
                    == snapshot.source_system,
                    MailDashboardRecord.mailbox
                    == snapshot.mailbox,
                    MailDashboardRecord.source_mail_id
                    == snapshot.source_mail_id,
                    MailDashboardRecord.state_changed_at
                    <= incoming_timestamp.isoformat(
                        timespec="microseconds",
                    ),
                )
                .values(
                    **values,
                    updated_at=now,
                )
            )
            update_result = session.execute(update_statement)
            session.commit()
            if update_result.rowcount:
                return MailDashboardUpsertResult(
                    status="updated",
                    changed=True,
                )

            return MailDashboardUpsertResult(
                status="stale",
                changed=False,
            )

    def get_summary(
        self,
        now: datetime | None = None,
    ) -> dict:
        self.ensure_schema()
        current_time = now or datetime.now(timezone.utc)
        if (
            current_time.tzinfo is None
            or current_time.utcoffset() is None
        ):
            raise ValueError("Summary time must include a timezone")

        current_time = current_time.astimezone(timezone.utc)
        now_text = current_time.isoformat(
            timespec="microseconds",
        )
        start_text = (
            current_time - timedelta(hours=24)
        ).isoformat(
            timespec="microseconds",
        )

        with SessionLocal() as session:
            counts = session.execute(
                select(
                    func.count().label("total_mail"),
                    func.sum(
                        case(
                            (
                                MailDashboardRecord.processing_state
                                == "SUCCESS",
                                1,
                            ),
                            else_=0,
                        )
                    ).label("successful_mail"),
                    func.sum(
                        case(
                            (
                                MailDashboardRecord.processing_state.in_(
                                    FAILED_MAIL_STATES
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ).label("failed_mail"),
                    func.sum(
                        case(
                            (
                                and_(
                                    MailDashboardRecord.received_at
                                    >= start_text,
                                    MailDashboardRecord.received_at
                                    <= now_text,
                                ),
                                1,
                            ),
                            else_=0,
                        )
                    ).label("mail_last_24h"),
                ).where(
                    MailDashboardRecord.source_system
                    == "mail-platform"
                )
            ).one()

            recent_failures = session.execute(
                select(
                    MailDashboardRecord.mailbox,
                    MailDashboardRecord.received_at,
                    MailDashboardRecord.subject,
                    MailDashboardRecord.processing_state,
                )
                .where(
                    MailDashboardRecord.source_system
                    == "mail-platform",
                    MailDashboardRecord.processing_state.in_(
                        FAILED_MAIL_STATES
                    ),
                )
                .order_by(
                    MailDashboardRecord.state_changed_at.desc(),
                    MailDashboardRecord.received_at.desc(),
                    MailDashboardRecord.source_system.asc(),
                    MailDashboardRecord.mailbox.asc(),
                    MailDashboardRecord.source_mail_id.asc(),
                )
                .limit(5)
            ).all()

            return {
                "total_mail": int(counts.total_mail or 0),
                "mail_last_24h": int(counts.mail_last_24h or 0),
                "failed_mail": int(counts.failed_mail or 0),
                "successful_mail": int(counts.successful_mail or 0),
                "recent_failed_mail": [
                    {
                        "mailbox": row.mailbox,
                        "received_at": (
                            datetime.fromisoformat(row.received_at)
                            if row.received_at
                            else None
                        ),
                        "subject": row.subject,
                        "processing_state": row.processing_state,
                    }
                    for row in recent_failures
                ],
            }
