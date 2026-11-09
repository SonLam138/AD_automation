import json
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from app.api import workflow_request
from app.auto_engine.models.employee_offboarding import (
    EmployeeOffboardingApiRequest,
)
from app.auto_engine.models.request_models import BulkConfirmRequest


class OffboardingRequestAuditFlowTests(unittest.TestCase):
    def setUp(self):
        self.request = EmployeeOffboardingApiRequest(
            employee_id="00012345",
            email="employee@example.com",
            reason="nghỉ việc",
            source_type="EMAIL",
            source_reference="<message@example.com>",
            source_request_id="mail-record-12",
        )
        self.parsed_request = SimpleNamespace(
            business_data={
                "target_object": {
                    "sam_account_name": "employee",
                }
            },
            request_id=None,
        )
        self.plan = SimpleNamespace(
            request_id="REQ-12",
            workflow_id="OFFBOARDING_RESIGNED",
            execute_at=datetime(2026, 1, 1, 9, 0),
        )

    def test_request_is_claimed_scheduled_and_mail_metadata_preserved(self):
        audit_record = SimpleNamespace(id=5)
        with (
            patch.object(
                workflow_request.employee_offboarding_api_adapter,
                "parse",
                return_value=self.parsed_request,
            ),
            patch.object(
                workflow_request.offboarding_audit_repository,
                "claim",
                return_value=(audit_record, True),
            ) as claim,
            patch.object(
                workflow_request.offboarding_audit_repository,
                "complete",
            ) as complete,
            patch.object(
                workflow_request.workflow_runtime,
                "run_plan_engine",
                return_value=self.plan,
            ) as run_plan,
            patch.object(
                workflow_request.access_snapshot_service,
                "save_snapshot",
            ),
            patch.object(
                workflow_request.mail_request_audit_repository,
                "get_by_request_id",
                return_value=None,
            ),
            patch.object(
                workflow_request.mail_request_audit_repository,
                "save",
            ) as save_mail_audit,
        ):
            result = workflow_request.create_offboarding_plan(
                self.request
            )

        self.assertEqual(result["request_id"], "REQ-12")
        self.assertEqual(
            claim.call_args.kwargs["source_request_id"],
            "mail-record-12",
        )
        self.assertEqual(
            run_plan.call_args.kwargs["source_data"][
                "source_request_id"
            ],
            "mail-record-12",
        )
        self.assertEqual(
            complete.call_args.kwargs["status"],
            "SCHEDULED",
        )
        self.assertEqual(
            save_mail_audit.call_args.args[0].source_reference,
            "<message@example.com>",
        )

    def test_duplicate_source_returns_cached_response_without_new_plan(self):
        cached_response = {
            "success": True,
            "request_id": "REQ-12",
            "workflow_id": "OFFBOARDING_RESIGNED",
        }
        existing_record = SimpleNamespace(
            id=5,
            employee_id="00012345",
            requested_account="employee",
            status="SCHEDULED",
            response_json=json.dumps(cached_response),
            response_status=200,
        )
        with (
            patch.object(
                workflow_request.employee_offboarding_api_adapter,
                "parse",
                return_value=self.parsed_request,
            ),
            patch.object(
                workflow_request.offboarding_audit_repository,
                "claim",
                return_value=(existing_record, False),
            ),
            patch.object(
                workflow_request.workflow_runtime,
                "run_plan_engine",
            ) as run_plan,
            patch.object(
                workflow_request.mail_request_audit_repository,
                "get_by_request_id",
                return_value=SimpleNamespace(request_id="REQ-12"),
            ),
        ):
            result = workflow_request.create_offboarding_plan(
                self.request
            )

        self.assertEqual(result, cached_response)
        run_plan.assert_not_called()

    def test_excel_confirmation_creates_audited_stable_requests(self):
        session = {
            "request_candidates": [
                {
                    "employee_id": "00012345",
                    "email": "employee@example.com",
                    "reason": "nghỉ việc",
                    "effective_time": "2026-01-01",
                }
            ]
        }
        with (
            patch.object(
                workflow_request.review_session_repository,
                "get",
                return_value=session,
            ),
            patch.object(
                workflow_request.review_session_repository,
                "save",
            ),
            patch.object(
                workflow_request,
                "create_offboarding_plan",
            ) as create_plan,
        ):
            workflow_request.confirm_offboarding(
                BulkConfirmRequest(session_id="review-123")
            )

        submitted_request = create_plan.call_args.args[0]
        self.assertEqual(
            submitted_request.source_request_id,
            "OFFBOARDING-EXCEL-review-123-0",
        )
        self.assertEqual(submitted_request.source_type, "EXCEL")


if __name__ == "__main__":
    unittest.main()
