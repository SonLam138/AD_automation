import unittest
from datetime import datetime

from app.auto_engine.models.employee_onboarding_adapter import (
    EmployeeOnboardingApiAdapter,
)
from app.auto_engine.models.request_models import (
    RequestContext,
)
from app.auto_engine.models.request_type import RequestType
from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver,
)
from app.models.ad_tool import CreateAdUserRequest


class EmployeeOnboardingApiAdapterTests(unittest.TestCase):

    def setUp(self):
        self.source_data = {
            "source_request_id": "MAIL-REQ-123",
            "employee_id": "E123",
            "first_name": "A",
            "last_name": "User",
            "full_name": "A User",
            "sam_account_name": "auser",
            "target_ou_dn": "OU=Users,DC=example,DC=com",
            "title": "Engineer",
            "department": "IT",
            "groups": ["Staff"],
        }

    def test_request_model_accepts_missing_or_explicit_onprem_flag(self):
        request = CreateAdUserRequest.model_validate(
            self.source_data
        )
        self.assertIsNone(request.is_onprem)

        request_with_flag = CreateAdUserRequest.model_validate(
            {
                **self.source_data,
                "is_onprem": False,
            }
        )
        self.assertFalse(request_with_flag.is_onprem)

    def test_adapter_builds_newbie_request_and_trigger_data(self):
        request = EmployeeOnboardingApiAdapter().parse(
            self.source_data
        )

        self.assertEqual(
            request.request_type,
            RequestType.EMPLOYEE_ONBOARDING,
        )
        self.assertEqual(
            request.context,
            RequestContext.NEWBIE,
        )
        self.assertEqual(
            request.source.source_reference,
            "MAIL-REQ-123",
        )
        self.assertEqual(
            request.business_data["source_request_id"],
            "MAIL-REQ-123",
        )
        self.assertEqual(
            request.business_data["display_name"],
            "A User",
        )
        self.assertIsNone(
            request.business_data["user_principal_name"]
        )
        self.assertIsNone(
            request.business_data["license_sku_id"]
        )
        self.assertEqual(
            request.business_data["disabled_plan_ids"],
            [],
        )
        self.assertIsInstance(
            request.business_data["start_date"],
            datetime,
        )
        self.assertNotIn(
            "password",
            request.business_data,
        )
        workflow = WorkflowResolver().resolve(
            request
        )
        self.assertEqual(
            workflow.workflow_id,
            "NEW_ONBOARDING",
        )

    def test_adapter_preserves_graph_license_parameters(self):
        request = EmployeeOnboardingApiAdapter().parse(
            {
                **self.source_data,
                "user_principal_name": "auser@example.com",
                "license_sku_id": "sku-guid",
                "disabled_plan_ids": ["plan-guid"],
            }
        )

        self.assertEqual(
            request.business_data["user_principal_name"],
            "auser@example.com",
        )
        self.assertEqual(
            request.business_data["license_sku_id"],
            "sku-guid",
        )
        self.assertEqual(
            request.business_data["disabled_plan_ids"],
            ["plan-guid"],
        )

    def test_adapter_temporarily_uses_onprem_context_even_if_flag_false(self):
        request = EmployeeOnboardingApiAdapter().parse(
            {
                **self.source_data,
                "is_onprem": False,
            }
        )

        self.assertEqual(
            request.context,
            RequestContext.NEWBIE,
        )

    def test_adapter_rejects_missing_required_request_ids(self):
        for field in ("source_request_id", "employee_id"):
            source_data = dict(self.source_data)
            source_data[field] = " "
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    EmployeeOnboardingApiAdapter().parse(
                        source_data
                    )


if __name__ == "__main__":
    unittest.main()
