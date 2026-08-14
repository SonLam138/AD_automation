from typing import Callable, Dict

from app.auto_engine.models.job import (
    Job,
)
from app.auto_engine.models.action_result import (
    ActionResult,
)


ActionExecutor = Callable[
    [Job],
    ActionResult,
]


class ActionExecutorRegistry:

    def __init__(
        self,
    ):
        self._executors: Dict[
            str,
            ActionExecutor,
        ] = {}

    def register(
        self,
        action_code: str,
        executor: ActionExecutor,
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
            self._executors
        ):
            raise ValueError(
                "Executor đã được đăng ký: "
                f"{normalized_action_code}"
            )

        self._executors[
            normalized_action_code
        ] = executor

    def get(
        self,
        action_code: str,
    ) -> ActionExecutor:

        normalized_action_code = (
            action_code
            .strip()
            .lower()
        )

        executor = self._executors.get(
            normalized_action_code
        )

        if executor is None:
            raise ValueError(
                "Không tìm thấy executor cho "
                f"action_code: "
                f"{normalized_action_code}"
            )

        return executor

    def contains(
        self,
        action_code: str,
    ) -> bool:

        normalized_action_code = (
            action_code
            .strip()
            .lower()
        )

        return (
            normalized_action_code
            in self._executors
        )