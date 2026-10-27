import unittest
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auto_engine.sqlite.base import Base
from app.auth.integration_registry import INTEGRATION_CLIENTS
from app.auth.jwt_handler import (
    create_access_token,
    create_integration_token,
)
from app.mail_dashboard.record import MailDashboardRecord
from app.api import mail_dashboard_controller
from app.mail_dashboard import repository as repository_module
from app.mail_dashboard import service as service_module


class MailDashboardApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )
        self.engine_patch = patch.object(
            repository_module,
            "engine",
            self.engine,
        )
        self.session_patch = patch.object(
            repository_module,
            "SessionLocal",
            self.session_factory,
        )
        self.refresh_publisher = patch.object(
            service_module,
            "publish_monitor_refresh",
        )
        self.engine_patch.start()
        self.session_patch.start()
        self.refresh_mock = self.refresh_publisher.start()
        MailDashboardRecord.__table__.create(
            bind=self.engine,
            checkfirst=True,
        )

        app = FastAPI()
        app.include_router(
            mail_dashboard_controller.router,
            prefix="/mail-dashboard",
        )
        self.client = TestClient(app)
        self.headers = {
            "Authorization": (
                "Bearer "
                + create_integration_token("mail-platform")
            )
        }
        self.user_headers = {
            "Authorization": (
                "Bearer "
                + create_access_token(
                    {
                        "username": "dashboard-user",
                        "display_name": "Dashboard User",
                        "groups": ["ad_login"],
                    }
                )
            )
        }

    def tearDown(self):
        self.client.close()
        self.refresh_publisher.stop()
        self.session_patch.stop()
        self.engine_patch.stop()
        self.engine.dispose()

    @staticmethod
    def snapshot(
        state="PENDING",
        state_changed_at="2026-10-22T10:00:00Z",
        subject="Initial subject",
    ):
        return {
            "schema_version": 1,
            "source_system": "mail-platform",
            "mailbox": " SHARED-MAILBOX@example.com ",
            "source_mail_id": "message-001",
            "subject": subject,
            "received_at": "2026-10-22T09:55:00Z",
            "processing_state": state,
            "state_changed_at": state_changed_at,
        }

    def post_snapshot(self, payload):
        return self.client.post(
            "/mail-dashboard/snapshots",
            json=payload,
            headers=self.headers,
        )

    def test_create_and_duplicate_are_idempotent(self):
        first = self.post_snapshot(self.snapshot())
        duplicate = self.post_snapshot(self.snapshot())

        self.assertEqual(first.status_code, 200)
        self.assertEqual(
            first.json(),
            {"status": "created", "changed": True},
        )
        self.assertEqual(
            duplicate.json(),
            {"status": "unchanged", "changed": False},
        )
        self.refresh_mock.assert_called_once_with()

        with self.session_factory() as session:
            records = session.execute(
                select(MailDashboardRecord)
            ).scalars().all()

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0].mailbox,
            "shared-mailbox@example.com",
        )

    def test_newer_state_updates_and_stale_state_is_ignored(self):
        self.post_snapshot(self.snapshot())

        updated = self.post_snapshot(
            self.snapshot(
                state="SUCCESS",
                state_changed_at="2026-10-22T10:05:00Z",
                subject="Updated subject",
            )
        )
        stale = self.post_snapshot(
            self.snapshot(
                state="RETRY_PENDING",
                state_changed_at="2026-10-22T10:03:00Z",
            )
        )

        self.assertEqual(
            updated.json(),
            {"status": "updated", "changed": True},
        )
        self.assertEqual(
            stale.json(),
            {"status": "stale", "changed": False},
        )
        self.assertEqual(self.refresh_mock.call_count, 2)

        with self.session_factory() as session:
            record = session.execute(
                select(MailDashboardRecord)
            ).scalar_one()

        self.assertEqual(record.processing_state, "SUCCESS")
        self.assertEqual(record.subject, "Updated subject")

    def test_conflicting_state_at_same_timestamp_returns_conflict(self):
        self.post_snapshot(self.snapshot())
        response = self.post_snapshot(
            self.snapshot(
                state="SUCCESS",
                state_changed_at="2026-10-22T10:00:00Z",
            )
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.refresh_mock.call_count, 1)

    def test_same_state_cannot_advance_state_changed_at(self):
        self.post_snapshot(self.snapshot())
        response = self.post_snapshot(
            self.snapshot(
                state="PENDING",
                state_changed_at="2026-10-22T10:01:00Z",
            )
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.refresh_mock.call_count, 1)

    def test_integration_client_must_have_snapshot_capability(self):
        allowed_endpoints = INTEGRATION_CLIENTS["mail-platform"][
            "allowed_endpoints"
        ]
        INTEGRATION_CLIENTS["mail-platform"]["allowed_endpoints"] = []
        try:
            response = self.post_snapshot(self.snapshot())
        finally:
            INTEGRATION_CLIENTS["mail-platform"][
                "allowed_endpoints"
            ] = allowed_endpoints

        self.assertEqual(response.status_code, 403)
        self.refresh_mock.assert_not_called()

    def test_authentication_and_payload_validation(self):
        unauthorized = self.client.post(
            "/mail-dashboard/snapshots",
            json=self.snapshot(),
        )
        invalid_state = self.post_snapshot(
            self.snapshot(state="UNKNOWN")
        )
        naive_timestamp = self.snapshot()
        naive_timestamp["state_changed_at"] = "2026-10-22T10:00:00"
        invalid_timestamp = self.post_snapshot(naive_timestamp)

        self.assertEqual(unauthorized.status_code, 401)
        self.assertEqual(invalid_state.status_code, 422)
        self.assertEqual(invalid_timestamp.status_code, 422)
        self.refresh_mock.assert_not_called()

    def add_snapshot_record(
        self,
        *,
        mailbox,
        source_mail_id,
        state,
        received_at,
        state_changed_at,
        subject=None,
        source_system="mail-platform",
    ):
        with self.session_factory() as session:
            session.add(
                MailDashboardRecord(
                    source_system=source_system,
                    mailbox=mailbox,
                    source_mail_id=source_mail_id,
                    subject=subject or source_mail_id,
                    received_at=(
                        received_at.isoformat(
                            timespec="microseconds",
                        )
                        if received_at
                        else None
                    ),
                    processing_state=state,
                    state_changed_at=state_changed_at.isoformat(
                        timespec="microseconds",
                    ),
                    created_at=state_changed_at.isoformat(
                        timespec="microseconds",
                    ),
                    updated_at=state_changed_at.isoformat(
                        timespec="microseconds",
                    ),
                )
            )
            session.commit()

    def test_summary_counts_states_and_rolling_24_hour_boundaries(self):
        now = datetime(
            2026,
            10,
            22,
            12,
            0,
            tzinfo=timezone.utc,
        )
        recent_time = now - timedelta(hours=2)
        boundary_start = now - timedelta(hours=24)
        future_time = now + timedelta(seconds=1)
        just_outside_window = boundary_start - timedelta(microseconds=1)
        records = [
            ("SUCCESS", recent_time, "success-recent"),
            ("SUCCESS", boundary_start, "success-boundary"),
            ("SUCCESS", now, "success-at-now"),
            ("RETRY_PENDING", recent_time, "failed-recent"),
            ("BUSINESS_REJECTED", None, "failed-no-date"),
            ("INVALID_REQUEST", recent_time, "failed-invalid"),
            ("UNSUPPORTED_REQUEST", future_time, "failed-future"),
            ("RETRY_EXHAUSTED", recent_time, "failed-exhausted"),
            ("PENDING", recent_time, "pending"),
            ("PROCESSING", recent_time, "processing"),
            ("PROCESSING", just_outside_window, "outside-window"),
        ]
        for index, (state, received_at, mail_id) in enumerate(records):
            self.add_snapshot_record(
                mailbox="shared@example.com",
                source_mail_id=mail_id,
                state=state,
                received_at=received_at,
                state_changed_at=now - timedelta(minutes=index),
            )

        summary = repository_module.MailDashboardRepository().get_summary(
            now=now,
        )

        self.assertEqual(summary["total_mail"], 11)
        self.assertEqual(summary["mail_last_24h"], 8)
        self.assertEqual(summary["successful_mail"], 3)
        self.assertEqual(summary["failed_mail"], 5)
        self.assertEqual(len(summary["recent_failed_mail"]), 5)
        self.assertNotIn("body", summary["recent_failed_mail"][0])

    def test_summary_returns_only_five_latest_failures_with_tie_breakers(self):
        now = datetime(
            2026,
            10,
            22,
            12,
            0,
            tzinfo=timezone.utc,
        )
        tied_time = now - timedelta(minutes=1)
        tied_failures = [
            ("c-mail", timedelta(minutes=5)),
            ("a-mail", timedelta(minutes=5)),
            ("b-mail", timedelta(minutes=1)),
        ]
        for mail_id, received_delta in tied_failures:
            self.add_snapshot_record(
                mailbox="shared@example.com",
                source_mail_id=mail_id,
                state="RETRY_PENDING",
                received_at=now - received_delta,
                state_changed_at=tied_time,
                subject=mail_id,
            )

        for index in range(3):
            self.add_snapshot_record(
                mailbox="shared@example.com",
                source_mail_id=f"newest-{index}",
                state="INVALID_REQUEST",
                received_at=now - timedelta(minutes=index),
                state_changed_at=now - timedelta(seconds=index),
                subject=f"newest-{index}",
            )

        result = repository_module.MailDashboardRepository().get_summary(
            now=now,
        )

        self.assertEqual(len(result["recent_failed_mail"]), 5)
        self.assertEqual(
            [
                row["subject"]
                for row in result["recent_failed_mail"]
            ],
            [
                "newest-0",
                "newest-1",
                "newest-2",
                "b-mail",
                "a-mail",
            ],
        )

    def test_summary_endpoint_requires_ad_login_group(self):
        no_token = self.client.get(
            "/mail-dashboard/summary",
        )
        wrong_group = self.client.get(
            "/mail-dashboard/summary",
            headers={
                "Authorization": (
                    "Bearer "
                    + create_access_token(
                        {
                            "username": "other-user",
                            "display_name": "Other User",
                            "groups": ["Domain Users"],
                        }
                    )
                )
            },
        )
        allowed = self.client.get(
            "/mail-dashboard/summary",
            headers=self.user_headers,
        )

        self.assertEqual(no_token.status_code, 401)
        self.assertEqual(wrong_group.status_code, 403)
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(
            allowed.json(),
            {
                "total_mail": 0,
                "mail_last_24h": 0,
                "failed_mail": 0,
                "successful_mail": 0,
                "recent_failed_mail": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
