import random
from datetime import datetime, time, timedelta

from app.auto_engine.models.execution_plan import ExecutionPlan


class PlanGenerator:
    @staticmethod
    def _get_scheduled_execute_at(
        trigger_value: datetime,
        schedule_policy: dict,
        now: datetime | None = None,
    ) -> datetime:
        if not isinstance(trigger_value, datetime):
            raise ValueError(
                "Workflow trigger value must be a datetime"
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