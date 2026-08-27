from abc import ABC, abstractmethod
from typing import Any, Dict

from app.adapters.ldap_container import (
    ldap,
)


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
            raise ValueError(
                f"DEBUG ==> {business_data}"
            )

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
                "group_name"
            )
            or parameters.get(
                "target_group"
            )
            or parameters.get(
                "target_group_name"
            )
            or parameters.get(
            "targetGroup"
            )
        )

        if not group_name:
            raise ValueError(
                "Thiếu group_name trong "
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

            self.ldap_service.remove_group_member(
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

    # @staticmethod
    # def _get_sam_account_name(
    #     business_data: Dict[str, Any],
    # ) -> str:

    #     target_object = (
    #         business_data.get(
    #             "target_object"
    #         )
    #         or {}
    #     )

    #     sam_account_name = (
    #         target_object.get(
    #             "sam_account_name"
    #         )
    #         or business_data.get(
    #             "sam_account_name"
    #         )
    #     )

    #     if not sam_account_name:
    #         raise ValueError(
    #             "Thiếu "
    #             "target_object.sam_account_name "
    #             "trong business_data"
    #         )

    #     return sam_account_name

    # @staticmethod
    # def _get_target_ou(
    #     business_data: Dict[str, Any],
    # ) -> str:

    #     action_data = (
    #         business_data.get(
    #             "action_data"
    #         )
    #         or {}
    #     )

    #     target_ou = (
    #         action_data.get(
    #             "target_ou"
    #         )
    #         or action_data.get(
    #             "target_ou_dn"
    #         )
    #         or business_data.get(
    #             "target_ou"
    #         )
    #         or business_data.get(
    #             "target_ou_dn"
    #         )
    #     )

    #     if not target_ou:
    #         raise ValueError(
    #             "Thiếu target OU trong "
    #             "business_data.action_data"
    #         )

    #     return target_ou

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
