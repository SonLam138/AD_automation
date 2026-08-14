from app.auto_engine.services.plan_runner import (
    PlanRunner
)

from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository
)


REQUEST_ID = "REQ_10082026_E2B9"


repo = ActiveExecutionRepository()
runner = PlanRunner()


def print_ready_actions(
    title: str,
    active_execution
):
    actions = runner.get_ready_actions(
        active_execution
    )

    print(f"\n{title}")

    if not actions:
        print("NO READY ACTION")

    for action in actions:
        print(
            action.id,
            action.action_code
        )

    return actions


# ==================================================
# CASE 1
# ==================================================

active_execution = repo.get(
    REQUEST_ID
)

active_execution.completed_action_ids = []

actions = print_ready_actions(
    "CASE 1 - NOTHING COMPLETED",
    active_execution
)

assert len(actions) == 1
assert actions[0].id == "STEP_01"


# ==================================================
# CASE 2
# ==================================================

active_execution.completed_action_ids = [
    "STEP_01"
]

actions = print_ready_actions(
    "CASE 2 - STEP_01 COMPLETED",
    active_execution
)

assert len(actions) == 1
assert actions[0].id == "STEP_02"


# ==================================================
# CASE 3
# ==================================================

active_execution.completed_action_ids = [
    "STEP_01",
    "STEP_02"
]

actions = print_ready_actions(
    "CASE 3 - STEP_01 STEP_02 COMPLETED",
    active_execution
)

assert len(actions) == 1
assert actions[0].id == "STEP_03"


# ==================================================
# CASE 4
# ==================================================

active_execution.completed_action_ids = [
    "STEP_01",
    "STEP_02",
    "STEP_03"
]

actions = print_ready_actions(
    "CASE 4 - ALL COMPLETED",
    active_execution
)

assert len(actions) == 0


print("\nPLAN RUNNER TEST PASSED")