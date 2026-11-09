import csv
import io
import unittest
from datetime import datetime
from types import SimpleNamespace

from app.auto_engine.report.mail_request_report import MailRequestReport
from app.auto_engine.report.mail_request_report_service import (
    MailRequestReportService,
)


class OffboardingAuditReportTests(unittest.TestCase):
    def test_summary_and_csv_include_offboarding_audit(self):
        record = SimpleNamespace(
            source_request_id="mail-42",
            employee_id="00012345",
            requested_account="employee",
            actual_account="employee",
            status="FAILED",
            step_outcomes_json=(
                '[{"step":"remove_all_groups","success":false,'
                '"duration_ms":12,"started_at":"2026-01-01T00:00:00",'
                '"completed_at":"2026-01-01T00:00:01"}]'
            ),
        )
        report = MailRequestReport(
            total_requests=0,
            emergency_requests=0,
            workflow_summary=[],
            reason_summary=[],
            period_start=datetime(2026, 1, 1),
            period_end=datetime(2026, 1, 2),
            details=[],
            offboarding_total=1,
            offboarding_failed=1,
            offboarding_details=[record],
        )
        service = MailRequestReportService()

        csv_rows = list(
            csv.reader(
                io.StringIO(
                    service.export_offboarding_csv_content(report)
                )
            )
        )
        summary = service.to_text(report, "Report")

        self.assertEqual(csv_rows[0][0], "source_request_id")
        self.assertEqual(csv_rows[1][0], "mail-42")
        self.assertEqual(csv_rows[1][5], "remove_all_groups")
        self.assertIn("Tổng số yêu cầu offboarding: 1", summary)
        self.assertIn("FAILED: 1", summary)


if __name__ == "__main__":
    unittest.main()
