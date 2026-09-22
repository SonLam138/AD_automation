import random
from datetime import datetime, time, timedelta

from app.auto_engine.models.execution_plan import ExecutionPlan


class PlanGenerator:
    @staticmethod
    def _normalize_trigger_datetime(
        trigger_value,
    ) -> datetime:
        if isinstance(trigger_value, datetime):
            return trigger_value

        if isinstance(trigger_value, str):
            normalized_value = trigger_value.strip()

            if normalized_value.endswith("Z"):
                normalized_value = (
                    normalized_value[:-1]
                    + "+00:00"
                )

            try:
                return datetime.fromisoformat(
                    normalized_value
                )
            except ValueError as exc:
                raise ValueError(
                    "Workflow trigger value must be "
                    "a valid ISO datetime"
                ) from exc

        raise ValueError(
            "Workflow trigger value must be a datetime"
        )

    @staticmethod
    def _get_scheduled_execute_at(
        trigger_value,
        schedule_policy: dict,
        now: datetime | None = None,
    ) -> datetime:
        trigger_value = (
            PlanGenerator._normalize_trigger_datetime(
                trigger_value
            )
        )

        current_time = now or datetime.now()
        start_hour = schedule_policy["start_hour"]
        end_hour = schedule_policy["end_hour"]
        window_minutes = (
            (end_hour - start_hour) * 60
        )
        random_minute = random.randint(
            0,
            window_minutes,
        )
        execute_at = (
            trigger_value.replace(
                hour=start_hour,
                minute=0,
                second=0,
                microsecond=0,
            )
            + timedelta(
                minutes=random_minute
            )
        )

        if current_time.time() > time(
            hour=end_hour,
        ):
            execute_at += timedelta(days=1)

        return execute_at

    def generate(
        self,
        request,
        workflow
    ) -> ExecutionPlan:

        trigger_field = workflow.metadata.get("trigger_field")

        trigger_value = request.business_data[trigger_field]
        is_emergency = bool(
            request.business_data.get(
                "is_emergency",
                False,
            )
        )
        emergency_execute_at = (
            request.business_data.get(
                "emergency_execute_at"
            )
        )

        if is_emergency:
            if emergency_execute_at is None:
                raise ValueError(
                    "emergency_execute_at is required "
                    "for emergency workflow request"
                )

            execute_at = (
                self._normalize_trigger_datetime(
                    emergency_execute_at
                )
            )

            return ExecutionPlan(
                request_id=request.request_id,
                workflow_id=workflow.workflow_id,
                execute_at=execute_at,
                actions=workflow.actions,
                business_data=request.business_data
            )

        schedule_policy = workflow.metadata.get(
            "schedule_policy"
        )

        if schedule_policy:
            execute_at = self._get_scheduled_execute_at(
                trigger_value=trigger_value,
                schedule_policy=schedule_policy,
            )
        else:
            execute_at = trigger_value

        return ExecutionPlan(
            request_id=request.request_id,
            workflow_id=workflow.workflow_id,
            execute_at=execute_at,
            actions=workflow.actions,
            business_data=request.business_data
        )