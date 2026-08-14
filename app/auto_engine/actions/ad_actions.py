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

    @staticmethod
    def _get_sam_account_name(
        business_data: Dict[str, Any],
    ) -> str:
        """
        Ưu tiên target_object theo nguyên tắc
        Object First.

        Tạm hỗ trợ sam_account_name ở root để
        tương thích dữ liệu cũ.
        """

        target_object = (
            business_data.get(
                "target_object"
            )
            or {}
        )

        sam_account_name = (
            target_object.get(
                "sam_account_name"
            )
            or business_data.get(
                "sam_account_name"
            )
        )

        if not sam_account_name:
            raise ValueError(
                "Thiếu "
                "target_object.sam_account_name "
                "trong business_data"
            )

        return sam_account_name


class MoveToOuAction(
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

    @staticmethod
    def _get_sam_account_name(
        business_data: Dict[str, Any],
    ) -> str:

        target_object = (
            business_data.get(
                "target_object"
            )
            or {}
        )

        sam_account_name = (
            target_object.get(
                "sam_account_name"
            )
            or business_data.get(
                "sam_account_name"
            )
        )

        if not sam_account_name:
            raise ValueError(
                "Thiếu "
                "target_object.sam_account_name "
                "trong business_data"
            )

        return sam_account_name

    @staticmethod
    def _get_target_ou(
        business_data: Dict[str, Any],
    ) -> str:

        action_data = (
            business_data.get(
                "action_data"
            )
            or {}
        )

        target_ou = (
            action_data.get(
                "target_ou"
            )
            or action_data.get(
                "target_ou_dn"
            )
            or business_data.get(
                "target_ou"
            )
            or business_data.get(
                "target_ou_dn"
            )
        )

        if not target_ou:
            raise ValueError(
                "Thiếu target OU trong "
                "business_data.action_data"
            )

        return target_ou


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