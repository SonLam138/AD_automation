from datetime import datetime

from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)

from app.auto_engine.models.workflow_definition import (
    WorkflowAction,
    WorkflowExecution,
)

from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)

from app.auto_engine.services.runtime_scheduler import (
    RuntimeScheduler,
)


repo = ActiveExecutionRepository(
    storage_path="data/test_active_executions"
)


def create_test_action() -> WorkflowAction:
    return WorkflowAction(
        id="STEP_01",
        action_code="disable_user",
        display_name="Disable User",
        execution=WorkflowExecution(
            depends_on=[],
            delay_minutes=0,
            retry_count=3,
            continue_on_error=False,
        ),
    )


past_execution = ActiveExecution(
    request_id="REQ_DUE_001",
    workflow_id="TEST_WORKFLOW",
    execute_at=datetime(
        2026,
        8,
        9,
        10,
        0,
        0,
    ),
    actions=[
        create_test_action()
    ],
    status=ActiveExecutionStatus.SCHEDULED,
)


future_execution = ActiveExecution(
    request_id="REQ_FUTURE_001",
    workflow_id="TEST_WORKFLOW",
    execute_at=datetime(
        2026,
        8,
        11,
        10,
        0,
        0,
    ),
    actions=[
        create_test_action()
    ],
    status=ActiveExecutionStatus.SCHEDULED,
)


running_execution = ActiveExecution(
    request_id="REQ_RUNNING_001",
    workflow_id="TEST_WORKFLOW",
    execute_at=datetime(
        2026,
        8,
        9,
        9,
        0,
        0,
    ),
    actions=[
        create_test_action()
    ],
    status=ActiveExecutionStatus.RUNNING,
)


repo.save(past_execution)
repo.save(future_execution)
repo.save(running_execution)


scheduler = RuntimeScheduler(
    active_execution_repository=repo
)


test_now = datetime(
    2026,
    8,
    10,
    12,
    0,
    0,
)


due_executions = scheduler.get_due_executions(
    now=test_now
)


print("\nDUE EXECUTIONS")

for execution in due_executions:
    scheduler.mark_scheduled(
    execution.request_id
    )
    print(
        execution.request_id,
        execution.execute_at,
        execution.status,
    )


assert len(due_executions) == 1

assert (
    due_executions[0].request_id
    == "REQ_DUE_001"
)

print("\nRUNTIME SCHEDULER TEST PASSED")