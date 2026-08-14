from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)

from app.auto_engine.models.execution_plan import (
    ExecutionPlan,
)


class ActiveExecutionBuilder:

    def build(
        self,
        plan: ExecutionPlan,
    ) -> ActiveExecution:
        return ActiveExecution(
            request_id=plan.request_id,
            workflow_id=plan.workflow_id,
            execute_at=plan.execute_at,

            # Deep copy để ActiveExecution không dùng chung
            # object action trong RAM với ExecutionPlan.
            actions=[
                action.model_copy(deep=True)
                for action in plan.actions
            ],

            business_data=plan.business_data.copy(),

            status=ActiveExecutionStatus.SCHEDULED,
        )