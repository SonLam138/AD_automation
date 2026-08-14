from datetime import datetime

from app.auto_engine.services.execution_plan_repository import (
    ExecutionPlanRepository
)

from app.auto_engine.models.workflow_definition import (
    WorkflowAction,
    WorkflowExecution
)

from app.auto_engine.models.execution_plan import (
    ExecutionPlan
)

plan = ExecutionPlan(
    request_id="REQ_TEST_001",
    workflow_id="OFFBOARD_TERMINATION",
    execute_at=datetime.now(),
    actions=[
        WorkflowAction(
            action_id="disable_user",
            execution=WorkflowExecution()
        ),
        WorkflowAction(
            action_id="remove_groups",
            depends_on=["disable_user"],
            execution=WorkflowExecution()
        )
    ]
)

repo = ExecutionPlanRepository()

repo.save(plan)

print("SAVE OK")

loaded_plan = repo.get(
    "REQ_TEST_001"
)

print("\nLOADED PLAN")
print(loaded_plan)