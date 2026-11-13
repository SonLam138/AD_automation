import json
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auto_engine.sqlite import offboarding_audit_repository as repository_module
from app.auto_engine.sqlite.offboarding_audit_repository import (
    OffboardingAuditRepository,
)


class OffboardingAuditRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        engine = create_engine(
            f"sqlite:///{Path(self.temp_dir.name) / 'audit.db'}"
        )
        self.engine_patch = patch.object(
            repository_module,
            "engine",
            engine,
        )
        self.session_patch = patch.object(
            repository_module,
            "SessionLocal",
            sessionmaker(bind=engine, autoflush=False, autocommit=False),
        )
        self.engine_patch.start()
        self.session_patch.start()
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(engine.dispose)
        self.addCleanup(self.session_patch.stop)
        self.addCleanup(self.engine_patch.stop)
        self.repository = OffboardingAuditRepository()

    def test_claim_steps_and_terminal_status_are_persisted(self):
        record, created = self.repository.claim(
            source_request_id="mail-record-42",
            employee_id="00012345",
            requested_account="employee",
        )

        self.assertTrue(created)
        self.assertEqual(record.status, "IN_PROGRESS")

        started_at = datetime.utcnow()
        completed_at = started_at + timedelta(seconds=2)
        self.repository.record_step(
            audit_id=record.id,
            step_name="disable_user",
            success=False,
            started_at=started_at,
            completed_at=completed_at,
            details={"error": "dependency failed"},
        )
        self.repository.record_step(
            audit_id=record.id,
            step_name="disable_user",
            success=False,
            started_at=started_at,
            completed_at=completed_at,
            details={"error": "final dependency failure"},
        )
        self.repository.complete(
            audit_id=record.id,
            status="SCHEDULED",
            response={
                "success": True,
                "execute_at": completed_at,
            },
            response_status=200,
            actual_account="employee",
        )
        self.repository.finish(
            audit_id=record.id,
            status="FAILED",
            actual_account="employee",
        )

        saved = self.repository.get_by_source_request_id(
            "mail-record-42"
        )
        self.assertEqual(saved.status, "FAILED")
        self.assertEqual(saved.actual_account, "employee")
        self.assertEqual(saved.response_status, 200)
        self.assertEqual(
            len(json.loads(saved.step_outcomes_json)),
            1,
        )
        self.assertEqual(
            self.repository.count_between(
                datetime.utcnow() - timedelta(days=1),
                datetime.utcnow() + timedelta(days=1),
            ),
            1,
        )

    def test_claim_returns_existing_record_for_duplicate_source_id(self):
        first_record, created = self.repository.claim(
            "mail-record-99",
            "00099999",
            "employee99",
        )
        duplicate, duplicate_created = self.repository.claim(
            "mail-record-99",
            "00099999",
            "employee99",
        )

        self.assertTrue(created)
        self.assertFalse(duplicate_created)
        self.assertEqual(first_record.id, duplicate.id)


if __name__ == "__main__":
    unittest.main()
