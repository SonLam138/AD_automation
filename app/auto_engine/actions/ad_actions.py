from abc import ABC, abstractmethod
from typing import Any, Dict

from app.adapters.ldap_container import (
    ldap,
)
import requests
from datetime import datetime

from app.auth.jwt_handler import create_service_token
from app.audit.onboarding_audit import OnboardingAudit
from app.auto_engine.sqlite.onboarding_audit_repository import (
    OnboardingAuditRepository,
)
from app.models.ad_tool import CreateAdUserRequest

class BaseAdAction(ABC):

    @abstractmethod
    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @staticmethod
    def _get_target_business_data(
        business_data: Dict[str, Any],
    ) -> Dict[str, Any]:

        target_object = (
            business_data.get(
                "target_object"
            )
            or {}
        )

        # Schema mới
        target_business_data = (
            target_object.get(
                "business_data"
            )
            or {}
        )

        if target_business_data:
            return target_business_data

        # Backward compatibility
        return target_object

    @classmethod
    def _get_sam_account_name(
        cls,
        business_data: Dict[str, Any],
    ) -> str:

        target_business_data = (
            cls._get_target_business_data(
                business_data
            )
        )

        sam_account_name = (
            target_business_data.get(
                "sam_account_name"
            )
            or business_data.get(
                "sam_account_name"
            )
        )

        if not sam_account_name:
            raise ValueError(
                "Thiếu "
                "target_object.business_data."
                "sam_account_name"
            )

        return sam_account_name

    @staticmethod
    def _get_action_parameters(
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        action_data = (
            business_data.get(
                "action_data"
            )
            or {}
        )

        if not action_data:
            return {}

        execution_context = (
            execution_context
            or {}
        )

        action_id = (
            execution_context.get(
                "action_id"
            )
            or execution_context.get(
                "current_action_id"
            )
        )

        if action_id:

            parameters = (
                action_data.get(
                    action_id
                )
            )

            if parameters is None:
                raise ValueError(
                    "Không tìm thấy action_data "
                    f"cho action_id: {action_id}"
                )

            return parameters

        if len(action_data) == 1:

            return next(
                iter(
                    action_data.values()
                )
            )

        raise ValueError(
            "Không xác định được action_id "
            "trong execution_context"
        )

    @staticmethod
    def _execute_mail_platform_action(
        request_id: str,
        action_code: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        token = create_service_token()
        response = requests.post(
            "http://localhost:8001/api/v1/actions/execute",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "request_id": request_id,
                "action_code": action_code,
                "parameters": parameters,
            },
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        if not isinstance(result, dict):
            raise ValueError(
                "Mail Platform action response must be an object"
            )
        return result

    @staticmethod
    def _get_workflow_request_id(
        execution_context: Dict[str, Any] | None,
    ) -> str:
        request_id = (execution_context or {}).get(
            "request_id"
        )
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError(
                "request_id is required to call Mail Platform"
            )
        return request_id.strip()

    @classmethod
    def _get_group_name(
        cls,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> str:

        parameters = (
            cls._get_action_parameters(
                business_data,
                execution_context,
            )
        )

        group_name = (
            parameters.get(
                "target_group"
            )
            or parameters.get(
                "group_name"
            )
            or business_data.get(
                "target_group"
            )
            or business_data.get(
                "group_name"
            )
        )

        if not group_name:
            raise ValueError(
                "Thiếu target_group trong "
                "business_data.action_data"
            )

        return group_name

    @classmethod
    def _get_computer_name(
        cls,
        business_data: Dict[str, Any],
    ) -> str:

        target_business_data = (
            cls._get_target_business_data(
                business_data
            )
        )

        computer_name = (
            target_business_data.get(
                "computer_name"
            )
            or target_business_data.get(
                "sam_account_name"
            )
            or business_data.get(
                "computer_name"
            )
        )

        if not computer_name:
            raise ValueError(
                "Thiếu "
                "target_object.business_data."
                "computer_name"
            )

        computer_name = (
            computer_name.strip()
        )

        if computer_name.endswith(
            "$"
        ):
            computer_name = (
                computer_name[:-1]
            )

        return computer_name


    @classmethod
    def _get_target_ou(
        cls,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> str:

        parameters = (
            cls._get_action_parameters(
                business_data,
                execution_context,
            )
        )

        target_ou_dn = (
            parameters.get(
                "target_ou_dn"
            )

            or parameters.get(
                "target_ou"
            )

            # Custom Workflow
            or parameters.get(
                "targetOu"
            )

            or business_data.get(
                "target_ou_dn"
            )

            or business_data.get(
                "target_ou"
            )
        )

        if not target_ou_dn:
            raise ValueError(
                "Thiếu target_ou_dn trong "
                "business_data.action_data"
            )

        return target_ou_dn

# ==================================================
# USER ACTIONS
# ==================================================

class DisableUserAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        result = ldap.disable_user(
            sam_account_name
        )

        if isinstance(result, dict):
            return result

        return {
            "success": True,
            "action": "disable_user",
            "sam_account_name":
                sam_account_name,
            "execution_result": result,
        }


class CreateUserAction(BaseAdAction):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        source_request_id = business_data.get(
            "source_request_id"
        )
        if (
            not isinstance(source_request_id, str)
            or not source_request_id.strip()
        ):
            raise ValueError(
                "source_request_id is required for create_user"
            )

        request = CreateAdUserRequest(
            source_request_id=source_request_id.strip(),
            employee_id=business_data["employee_id"],
            first_name=business_data["first_name"],
            last_name=business_data["last_name"],
            full_name=business_data["full_name"],
            sam_account_name=business_data["sam_account_name"],
            display_name=business_data.get("display_name"),
            target_ou_dn=business_data["target_ou_dn"],
            title=business_data["title"],
            department=business_data["department"],
            description=business_data.get("description"),
            dry_run=bool(business_data.get("dry_run", False)),
            groups=business_data.get("groups", []),
            is_onprem=business_data.get("is_onprem"),
            user_principal_name=business_data.get(
                "user_principal_name"
            ),
            license_sku_id=business_data.get("license_sku_id"),
            disabled_plan_ids=business_data.get(
                "disabled_plan_ids",
                [],
            ),
        )

        audit_repository = OnboardingAuditRepository()
        audit_record = audit_repository.get_by_source_request_id(
            request.source_request_id
        )
        if audit_record is None:
            raise ValueError(
                "Onboarding audit record not found for "
                f"source_request_id={request.source_request_id}"
            )

        audit = OnboardingAudit(
            source_request_id=request.source_request_id,
            employee_id=request.employee_id,
            requested_account=request.sam_account_name,
            repository=audit_repository,
            audit_id=audit_record.id,
        )
        result = ldap.create_user(
            request,
            audit=audit,
        )
        if not isinstance(result, dict):
            raise RuntimeError(
                "LDAP create_user returned an invalid result"
            )
        return result


class OnpremDisableMailboxAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        action_data = (
            business_data["action_data"]
            ["STEP_MAILBOX"]
        )

        request_id = None

        if execution_context:

            request_id = (
                execution_context.get(
                    "request_id"
                )
            )

        token = create_service_token()

        headers = {

            "Authorization":
                f"Bearer {token}"
        }

        response = requests.post(

            "http://localhost:8001/api/v1/actions/execute",

            headers=headers,

            json={

                "request_id":
                    request_id,

                "action_code":
                    "ONPREM_DISABLE_MAILBOX",

                "parameters": {

                    "identity":
                        action_data["identity"]
                }
            },

            timeout=60,
        )

        response.raise_for_status()

        return response.json()


class OnpremCreateMailboxAction(BaseAdAction):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        source_request_id = business_data.get(
            "source_request_id"
        )
        if (
            not isinstance(source_request_id, str)
            or not source_request_id.strip()
        ):
            raise ValueError(
                "source_request_id is required for mailbox creation"
            )

        audit_repository = OnboardingAuditRepository()
        audit_record = audit_repository.get_by_source_request_id(
            source_request_id.strip()
        )
        if audit_record is None or not audit_record.actual_account:
            raise ValueError(
                "Resolved AD account is not available for mailbox creation"
            )

        audit = OnboardingAudit(
            source_request_id=source_request_id.strip(),
            employee_id=audit_record.employee_id,
            requested_account=audit_record.requested_account,
            repository=audit_repository,
            audit_id=audit_record.id,
        )
        audit.set_actual_account(
            audit_record.actual_account
        )
        started_at = datetime.utcnow()

        try:
            result = self._execute_mail_platform_action(
                request_id=self._get_workflow_request_id(
                    execution_context
                ),
                action_code="ONPREM_ENABLE_MAILBOX",
                parameters={
                    "identity": audit_record.actual_account,
                },
            )
        except Exception as ex:
            completed_at = datetime.utcnow()
            audit.record_step(
                step_name="onprem_create_mailbox",
                success=False,
                started_at=started_at,
                completed_at=completed_at,
                details={"error_type": type(ex).__name__},
            )
            audit.finish("FAILED")
            raise

        success = result.get("success") is True
        audit.record_step(
            step_name="onprem_create_mailbox",
            success=success,
            started_at=started_at,
            completed_at=datetime.utcnow(),
            details={
                "action_code": result.get("action_code"),
                "error": result.get("error"),
            },
        )
        audit.finish(
            "SUCCESS" if success else "FAILED"
        )
        return result


class OnlineCreateMailboxAction(BaseAdAction):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        user_principal_name = business_data.get(
            "user_principal_name"
        )
        if (
            not isinstance(user_principal_name, str)
            or not user_principal_name.strip()
        ):
            raise ValueError(
                "user_principal_name is required for online mailbox creation"
            )

        license_sku_id = business_data.get(
            "license_sku_id"
        )
        if (
            not isinstance(license_sku_id, str)
            or not license_sku_id.strip()
        ):
            raise ValueError(
                "license_sku_id is required for online mailbox creation"
            )

        disabled_plan_ids = business_data.get(
            "disabled_plan_ids",
            [],
        )
        if (
            not isinstance(disabled_plan_ids, list)
            or any(
                not isinstance(plan_id, str)
                or not plan_id.strip()
                for plan_id in disabled_plan_ids
            )
        ):
            raise ValueError(
                "disabled_plan_ids must be a list of non-empty strings"
            )

        return self._execute_mail_platform_action(
            request_id=self._get_workflow_request_id(
                execution_context
            ),
            action_code="ONLINE_ENABLE_MAILBOX",
            parameters={
                "user_principal_name": user_principal_name.strip(),
                "add_licenses": [
                    {
                        "sku_id": license_sku_id.strip(),
                        "disabled_plan_ids": [
                            plan_id.strip()
                            for plan_id in disabled_plan_ids
                        ],
                    },
                ],
                "remove_licenses": [],
            },
        )


class EnableUserAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        result = ldap.enable_user(
            sam_account_name
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,
            "action": "enable_user",
            "sam_account_name":
                sam_account_name,
            "execution_result":
                result,
        }

class AddGroupAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        group_name = (
            self._get_group_name(
                business_data,
                execution_context,
            )
        )

        result = (
            ldap.add_group_member(
                sam_account_name=
                    sam_account_name,
                group_name=
                    group_name,
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,
            "action": "add_group_member",
            "sam_account_name":
                sam_account_name,
            "group_name":
                group_name,
            "execution_result":
                result,
        }

class AddGroupByDnAction(
    BaseAdAction
):

    def execute(
        self,
        business_data:
            Dict[str, Any],

        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        group_dn = (
            self._get_group_name(
                business_data,
                execution_context,
            )
        )

        result = (
            ldap.add_group_member_by_dn(
                sam_account_name=
                    sam_account_name,

                group_dn=
                    group_dn,
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,

            "action":
                "add_group_member_by_dn",

            "sam_account_name":
                sam_account_name,

            "group_dn":
                group_dn,

            "execution_result":
                result,
        }


class RemoveGroupAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        group_name = (
            self._get_group_name(
                business_data,
                execution_context,
            )
        )

        result = (
            ldap.remove_group_member(
                sam_account_name=
                    sam_account_name,
                group_name=
                    group_name,
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,
            "action": "remove_group_member",
            "sam_account_name":
                sam_account_name,
            "group_name":
                group_name,
            "execution_result":
                result,
        }

class RemoveGroupByDnAction(
    BaseAdAction
):

    def execute(
        self,
        business_data:
            Dict[str, Any],

        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        group_dn = (
            self._get_group_name(
                business_data,
                execution_context,
            )
        )

        result = (
            ldap.remove_group_member_by_dn(
                sam_account_name=
                    sam_account_name,

                group_dn=
                    group_dn,
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,

            "action":
                "remove_group_member_by_dn",

            "sam_account_name":
                sam_account_name,

            "group_dn":
                group_dn,

            "execution_result":
                result,
        }



class RemoveAllGroupsAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        target_object = (
            business_data[
                "target_object"
            ]
        )

        sam_account_name = (
            target_object[
                "sam_account_name"
            ]
        )

        groups = (
            target_object.get(
                "member_of",
                []
            )
        )

        removed_groups = []

        for group_dn in groups:

            group_name = (
                group_dn
                .split(",")[0]
                .replace("CN=", "")
            )

            ldap.remove_group_member(
                sam_account_name=sam_account_name,
                group_name=group_name
            )

            removed_groups.append(
                group_name
            )

        return {
            "success": True,
            "removed_groups": removed_groups
        }


class MoveUserToOuAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        sam_account_name = (
            self._get_sam_account_name(
                business_data
            )
        )

        target_ou = self._get_target_ou(
            business_data
        )

        result = ldap.move_user_to_ou(
            sam_account_name,
            target_ou,
        )

        if isinstance(result, dict):
            return result

        return {
            "success": True,
            "action": "move_to_ou",
            "sam_account_name":
                sam_account_name,
            "target_ou": target_ou,
            "execution_result": result,
        }

# ==================================================
# COMPUTER ACTIONS
# ==================================================

class DisableComputerAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        computer_name = (
            self._get_computer_name(
                business_data
            )
        )

        result = (
            ldap.disable_computer(
                computer_name
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,
            "action":
                "disable_computer",
            "computer_name":
                computer_name,
            "execution_result":
                result,
        }

class MoveComputerToOuAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        computer_name = (
            self._get_computer_name(
                business_data
            )
        )

        target_ou_dn = (
            self._get_target_ou(
                business_data,
                execution_context,
            )
        )

        result = (
            ldap.move_computer_to_ou(
                computer_name=
                    computer_name,
                target_ou_dn=
                    target_ou_dn,
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,
            "action":
                "move_computer_to_ou",
            "computer_name":
                computer_name,
            "target_ou":
                target_ou_dn,
            "execution_result":
                result,
        }

# ==================================================
# GROUP ACTIONS
# ==================================================

class MoveGroupToOuAction(
    BaseAdAction
):

    def execute(
        self,
        business_data: Dict[str, Any],
        execution_context:
            Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:

        group_name = (
            self._get_group_name(
                business_data
            )
        )

        target_ou_dn = (
            self._get_target_ou(
                business_data,
                execution_context,
            )
        )

        result = (
            ldap.move_group_to_ou(
                group_name=
                    group_name,
                target_ou_dn=
                    target_ou_dn,
            )
        )

        if isinstance(
            result,
            dict
        ):
            return result

        return {
            "success": True,
            "action":
                "move_group_to_ou",
            "group_name":
                group_name,
            "target_ou":
                target_ou_dn,
            "execution_result":
                result,
        }








class AdActionRegistry:

    def __init__(
        self,
    ):
        self._actions: Dict[
            str,
            BaseAdAction,
        ] = {}

    def register(
        self,
        action_code: str,
        action: BaseAdAction,
    ) -> None:

        normalized_action_code = (
            action_code
            .strip()
            .lower()
        )

        if not normalized_action_code:
            raise ValueError(
                "action_code không được rỗng"
            )

        if normalized_action_code in (
            self._actions
        ):
            raise ValueError(
                "AD Action đã được đăng ký: "
                f"{normalized_action_code}"
            )

        self._actions[
            normalized_action_code
        ] = action

    def get(
        self,
        action_code: str,
    ) -> BaseAdAction:

        normalized_action_code = (
            action_code
            .strip()
            .lower()
        )

        action = self._actions.get(
            normalized_action_code
        )

        if action is None:
            raise ValueError(
                "Không tìm thấy AD Action: "
                f"{normalized_action_code}"
            )

        return action

    def contains(
        self,
        action_code: str,
    ) -> bool:

        return (
            action_code.strip().lower()
            in self._actions
        )
