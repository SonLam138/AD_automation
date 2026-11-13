import unittest
from unittest.mock import Mock, patch

from app.auto_engine.actions.ad_actions import (
    CreateUserAction,
    OnpremCreateMailboxAction,
    OnlineCreateMailboxAction,
)


class OnboardingMailboxActionTests(unittest.TestCase):

    def setUp(self):
        self.response = Mock()
        self.response.json.return_value = {
            "success": True,
            "action_code": "ONPREM_ENABLE_MAILBOX",
            "data": {
                "success": True,
                "identity": "auser",
            },
        }

    def test_onprem_action_calls_mail_enable_endpoint(self):
        audit_repository = Mock()
        audit_repository.get_by_source_request_id.return_value = Mock(
            id=42,
            actual_account="auser",
            employee_id="E123",
            requested_account="auser",
        )
        with (
            patch(
                "app.auto_engine.actions.ad_actions.create_service_token",
                return_value="service-token",
            ),
            patch(
                "app.auto_engine.actions.ad_actions."
                "OnboardingAuditRepository",
                return_value=audit_repository,
            ),
            patch(
                "app.auto_engine.actions.ad_actions.requests.post",
                return_value=self.response,
            ) as post,
        ):
            result = OnpremCreateMailboxAction().execute(
                business_data={
                    "source_request_id": "MAIL-REQ-123",
                    "sam_account_name": "auser",
                },
                execution_context={
                    "request_id": "REQ_ONBOARDING",
                },
            )

        self.assertEqual(result["success"], True)
        self.assertEqual(
            post.call_args.kwargs["json"],
            {
                "request_id": "REQ_ONBOARDING",
                "action_code": "ONPREM_ENABLE_MAILBOX",
                "parameters": {
                    "identity": "auser",
                },
            },
        )
        self.response.raise_for_status.assert_called_once_with()
        audit_repository.record_step.assert_called_once()
        audit_repository.finish.assert_called_once_with(
            audit_id=42,
            status="SUCCESS",
            actual_account="auser",
        )

    def test_onprem_action_uses_resolved_account_from_user_creation(self):
        audit_repository = Mock()
        audit_repository.get_by_source_request_id.return_value = Mock(
            id=42,
            actual_account="auser2",
            employee_id="E123",
            requested_account="auser",
        )
        with (
            patch(
                "app.auto_engine.actions.ad_actions.create_service_token",
                return_value="service-token",
            ),
            patch(
                "app.auto_engine.actions.ad_actions."
                "OnboardingAuditRepository",
                return_value=audit_repository,
            ),
            patch(
                "app.auto_engine.actions.ad_actions.requests.post",
                return_value=self.response,
            ) as post,
        ):
            OnpremCreateMailboxAction().execute(
                business_data={
                    "source_request_id": "MAIL-REQ-123",
                    "sam_account_name": "auser",
                },
                execution_context={
                    "request_id": "REQ_ONBOARDING",
                },
            )

        self.assertEqual(
            post.call_args.kwargs["json"]["parameters"]["identity"],
            "auser2",
        )

    def test_onprem_mail_failure_marks_onboarding_audit_failed(self):
        audit_repository = Mock()
        audit_repository.get_by_source_request_id.return_value = Mock(
            id=42,
            actual_account="auser",
            employee_id="E123",
            requested_account="auser",
        )
        response = Mock()
        response.raise_for_status.side_effect = RuntimeError(
            "Mail Platform unavailable"
        )
        with (
            patch(
                "app.auto_engine.actions.ad_actions.create_service_token",
                return_value="service-token",
            ),
            patch(
                "app.auto_engine.actions.ad_actions."
                "OnboardingAuditRepository",
                return_value=audit_repository,
            ),
            patch(
                "app.auto_engine.actions.ad_actions.requests.post",
                return_value=response,
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "Mail Platform unavailable",
            ):
                OnpremCreateMailboxAction().execute(
                    business_data={
                        "source_request_id": "MAIL-REQ-123",
                        "sam_account_name": "auser",
                    },
                    execution_context={
                        "request_id": "REQ_ONBOARDING",
                    },
                )

        audit_repository.record_step.assert_called_once()
        self.assertFalse(
            audit_repository.record_step.call_args.kwargs["success"]
        )
        audit_repository.finish.assert_called_once_with(
            audit_id=42,
            status="FAILED",
            actual_account="auser",
        )

    def test_online_action_sends_graph_license_parameters(self):
        with (
            patch(
                "app.auto_engine.actions.ad_actions.create_service_token",
                return_value="service-token",
            ),
            patch(
                "app.auto_engine.actions.ad_actions.requests.post",
                return_value=self.response,
            ) as post,
        ):
            OnlineCreateMailboxAction().execute(
                business_data={
                    "user_principal_name": "auser@example.com",
                    "license_sku_id": "sku-guid",
                    "disabled_plan_ids": ["plan-guid"],
                },
                execution_context={
                    "request_id": "REQ_ONBOARDING",
                },
            )

        self.assertEqual(
            post.call_args.kwargs["json"],
            {
                "request_id": "REQ_ONBOARDING",
                "action_code": "ONLINE_ENABLE_MAILBOX",
                "parameters": {
                    "user_principal_name": "auser@example.com",
                    "add_licenses": [
                        {
                            "sku_id": "sku-guid",
                            "disabled_plan_ids": ["plan-guid"],
                        },
                    ],
                    "remove_licenses": [],
                },
            },
        )

    def test_online_action_requires_upn_and_license(self):
        action = OnlineCreateMailboxAction()
        for business_data in (
            {"license_sku_id": "sku-guid"},
            {"user_principal_name": "auser@example.com"},
        ):
            with self.subTest(business_data=business_data):
                with self.assertRaises(ValueError):
                    action.execute(
                        business_data=business_data,
                        execution_context={
                            "request_id": "REQ_ONBOARDING",
                        },
                    )

    def test_mail_platform_failure_response_is_preserved(self):
        self.response.json.return_value = {
            "success": False,
            "error": "Mailbox already exists",
        }
        audit_repository = Mock()
        audit_repository.get_by_source_request_id.return_value = Mock(
            id=42,
            actual_account="auser",
            employee_id="E123",
            requested_account="auser",
        )
        with (
            patch(
                "app.auto_engine.actions.ad_actions.create_service_token",
                return_value="service-token",
            ),
            patch(
                "app.auto_engine.actions.ad_actions."
                "OnboardingAuditRepository",
                return_value=audit_repository,
            ),
            patch(
                "app.auto_engine.actions.ad_actions.requests.post",
                return_value=self.response,
            ),
        ):
            result = OnpremCreateMailboxAction().execute(
                business_data={
                    "source_request_id": "MAIL-REQ-123",
                    "sam_account_name": "auser",
                },
                execution_context={
                    "request_id": "REQ_ONBOARDING",
                },
            )

        self.assertFalse(result["success"])

    def test_actions_are_registered_without_mailbox_retry(self):
        from app.auto_engine.runtime.runtime_container import (
            action_registry,
        )
        from app.auto_engine.resolver.workflow_registry import (
            WORKFLOW_REGISTRY,
        )

        self.assertTrue(
            action_registry.contains("onprem_create_mailbox")
        )
        self.assertTrue(
            action_registry.contains("online_create_mailbox")
        )

        workflow = next(
            item
            for item in WORKFLOW_REGISTRY
            if item["workflow_id"] == "NEW_ONBOARDING"
        )
        self.assertEqual(
            workflow["actions"][1]["action_code"],
            "onprem_create_mailbox",
        )
        self.assertEqual(
            workflow["actions"][1]["execution"]["retry_count"],
            0,
        )

    def test_create_user_action_calls_ldap_with_correlated_audit(self):
        audit_record = Mock(id=42)
        with (
            patch(
                "app.auto_engine.actions.ad_actions."
                "OnboardingAuditRepository.get_by_source_request_id",
                return_value=audit_record,
            ),
            patch(
                "app.auto_engine.actions.ad_actions.ldap.create_user",
                return_value={
                    "success": True,
                    "actual_account": "auser",
                },
            ) as create_user,
        ):
            result = CreateUserAction().execute(
                business_data={
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
                },
                execution_context={
                    "request_id": "REQ_ONBOARDING",
                    "action_id": "STEP_01",
                },
            )

        self.assertTrue(result["success"])
        request = create_user.call_args.args[0]
        audit = create_user.call_args.kwargs["audit"]
        self.assertEqual(request.employee_id, "E123")
        self.assertEqual(request.groups, ["Staff"])
        self.assertEqual(audit.audit_id, 42)

    def test_create_user_action_requires_existing_submission_audit(self):
        with patch(
            "app.auto_engine.actions.ad_actions."
            "OnboardingAuditRepository.get_by_source_request_id",
            return_value=None,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "Onboarding audit record not found",
            ):
                CreateUserAction().execute(
                    business_data={
                        "source_request_id": "MAIL-REQ-123",
                        "employee_id": "E123",
                        "first_name": "A",
                        "last_name": "User",
                        "full_name": "A User",
                        "sam_account_name": "auser",
                        "target_ou_dn": "OU=Users,DC=example,DC=com",
                        "title": "Engineer",
                        "department": "IT",
                    },
                    execution_context={
                        "request_id": "REQ_ONBOARDING",
                    },
                )


if __name__ == "__main__":
    unittest.main()
