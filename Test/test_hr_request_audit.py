import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.auto_engine.sqlite import (
    mail_request_audit_repository as hr_repository_module,
    offboarding_audit_repository as offboarding_repository_module,
    onboarding_audit_repository as onboarding_repository_module,
)
from app.auto_engine.sqlite.mail_request_audit_record import (
    HRRequestAuditRecord,
)
from app.auto_engine.sqlite.mail_request_audit_repository import (
    HRRequestAuditRepository,
)
from app.auto_engine.sqlite.offboarding_audit_repository import (
    OffboardingAuditRepository,
)
from app.auto_engine.sqlite.onboarding_audit_repository import (
    OnboardingAuditRepository,
)


class HRRequestAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = create_engine(
            f"sqlite:///{Path(self.temp_dir.name) / 'audit.db'}"
        )
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(self.engine.dispose)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )
        self.patches = [
            patch.object(module, "engine", self.engine)
            for module in (
                hr_repository_module,
                onboarding_repository_module,
                offboarding_repository_module,
            )
        ]
        self.patches.extend(
            patch.object(module, "SessionLocal", self.session_factory)
            for module in (
                hr_repository_module,
                onboarding_repository_module,
                offboarding_repository_module,
            )
        )
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def test_onboarding_scheduled_plan_is_projected_by_source_id(self):
        repository = OnboardingAuditRepository()
        record, created = repository.claim(
            source_request_id="1042",
            employee_id="00001042",
            requested_account="employee1042",
        )
        self.assertTrue(created)

        repository.complete(
            audit_id=record.id,
            status="SCHEDULED",
            response={
                "success": True,
                "request_id": "PLAN-1042",
                "workflow_id": "EMPLOYEE_ONBOARDING",
            },
            response_status=202,
        )

        with self.session_factory() as session:
            saved = session.get(HRRequestAuditRecord, "1042")
        self.assertEqual(saved.plan_request_id, "PLAN-1042")
        self.assertEqual(saved.request_id, "PLAN-1042")
        self.assertEqual(saved.request_type, "EMPLOYEE_ONBOARDING")

    def test_offboarding_schedule_and_non_mail_source_scope(self):
        repository = OffboardingAuditRepository()
        record, created = repository.claim(
            source_request_id="2042",
            employee_id="00002042",
            requested_account="employee2042",
        )
        self.assertTrue(created)
        repository.complete(
            audit_id=record.id,
            status="SCHEDULED",
            response={
                "success": True,
                "request_id": "PLAN-2042",
                "workflow_id": "OFFBOARDING_RESIGNED",
            },
            response_status=200,
        )

        manual_record, manual_created = repository.claim(
            source_request_id="OFFBOARDING-EXCEL-session-0",
            employee_id="00002043",
            requested_account="employee2043",
        )
        self.assertTrue(manual_created)
        repository.complete(
            audit_id=manual_record.id,
            status="SCHEDULED",
            response={
                "success": True,
                "request_id": "PLAN-2043",
                "workflow_id": "OFFBOARDING_RESIGNED",
            },
            response_status=200,
        )

        with self.session_factory() as session:
            saved = session.get(HRRequestAuditRecord, "2042")
            excluded = session.get(
                HRRequestAuditRecord,
                "OFFBOARDING-EXCEL-session-0",
            )
        self.assertEqual(saved.plan_request_id, "PLAN-2042")
        self.assertIsNone(excluded)

    def test_unscheduled_request_is_not_written_and_legacy_table_is_dropped(self):
        with self.engine.begin() as connection:
            connection.execute(
                text("CREATE TABLE mail_request_audits (request_id TEXT)")
            )

        HRRequestAuditRepository().ensure_schema()

        table_names = set(inspect(self.engine).get_table_names())
        self.assertIn("HR_request_audits", table_names)
        self.assertNotIn("mail_request_audits", table_names)

        repository = OnboardingAuditRepository()
        record, _ = repository.claim(
            source_request_id="3042",
            employee_id="00003042",
            requested_account="employee3042",
        )
        repository.complete(
            audit_id=record.id,
            status="FAILED",
            response={"detail": "invalid"},
            response_status=400,
        )

        with self.session_factory() as session:
            saved = session.get(HRRequestAuditRecord, "3042")
        self.assertIsNone(saved)

    def test_plan_id_query_only_returns_mail_onboarding_and_offboarding(self):
        repository = HRRequestAuditRepository()
        repository.ensure_schema()
        for source_request_id, plan_id, request_type in (
            ("4042", "PLAN-4042", "EMPLOYEE_ONBOARDING"),
            ("5042", "PLAN-5042", "EMPLOYEE_OFFBOARDING"),
            ("6042", "PLAN-6042", "TEMP_ACCESS"),
        ):
            repository.save(
                HRRequestAuditRecord(
                    source_request_id=source_request_id,
                    plan_request_id=plan_id,
                    workflow_id=request_type,
                    request_type=request_type,
                    employee_id="00004042",
                    created_at=datetime.utcnow(),
                )
            )

        self.assertEqual(
            repository.get_scheduled_source_request_ids(
                ["4042", "5042", "6042", "missing"]
            ),
            ["4042", "5042"],
        )

    def test_non_mail_source_does_not_create_hr_report_audit(self):
        saved = HRRequestAuditRepository().save(
            HRRequestAuditRecord(
                source_request_id="OFFBOARDING-EXCEL-session-0",
                plan_request_id="PLAN-EXCEL",
                workflow_id="OFFBOARDING_RESIGNED",
                request_type="EMPLOYEE_OFFBOARDING",
                employee_id="00004042",
                created_at=datetime.utcnow(),
            )
        )
        self.assertIsNone(saved)


if __name__ == "__main__":
    unittest.main()
