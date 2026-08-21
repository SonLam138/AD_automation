# test_custom_runtime.py

import time

from app.auto_engine.runtime.runtime_container import (
    workflow_runtime
)

from app.auto_engine.models.custom_workflow_adapter import (
    CustomWorkflowAdapter
)

source_data = {
"workflow_id": "WF_1787284539271",
"workflow_context":
"CUSTOM_WF_1787284539271_VENDER_A",
"objects": [
{
"alias": "VENDER_A",
"objectType": "USER",
"employee_id": "123456"
}
]
}
adapter = CustomWorkflowAdapter()

requests = adapter.build_requests(
    source_data
)

print(
    f"\nREQUEST COUNT: {len(requests)}"
)

for request in requests:

    print("\n" + "=" * 80)
    print(
        f"REQUEST: {request.context}"
    )

    plan = (
        workflow_runtime
        .workflow_plan_engine
        .process(request)
    )

    print(
        f"PLAN: {plan.workflow_id}"
    )

    workflow_runtime.plan_to_active(
        plan
    )

    active = (
        workflow_runtime
        .active_execution_repository
        .get(plan.request_id)
    )

    print(
        f"ACTIVE: {active.request_id}"
    )

    print(
        f"EXECUTE_AT: "
        f"{active.execute_at}"
    )

time.sleep(30)