from app.auto_engine.models.wf_with_newvalue_adapter import (
    TargetObjectWithNewValueAdapter
)
from app.auto_engine.resolver.workflow_registry import WORKFLOW_REGISTRY
from app.auto_engine.resolver.workflow_resolver import WorkflowResolver
from app.auto_engine.resolver.workflow_plan_engine import WorkflowPlanEngine
from app.auto_engine.runtime.runtime_container import (
    workflow_plan_engine,
    workflow_runtime,
    scheduler
)
source_data = {
    "request_type":
        "temp_access_computer",

    "context":
        "TEMP_ACCESS_COMPUTER",

    "computer_name":
        "Client-01",

    "start_date":
        "2026-08-23T23:00:00",

    "step_execute_times": [
        {
            "step_id":
                "STEP_02",

            "execute_at":
                "2026-08-24T23:00:00"
        }
    ],

    "step_new_values": [
        {
            "step_id":
                "STEP_01",

            "parameter_name":
                "target_ou",

            "new_value":
                (
                    "OU=Disabled Account,"
                    "DC=automate,"
                    "DC=com,"
                    "DC=vn"
                )
        },

        {
            "step_id":
                "STEP_02",

            "parameter_name":
                "target_ou",

            "new_value":
                (
                    "OU=HO,"
                    "DC=automate,"
                    "DC=com,"
                    "DC=vn"
                )
        }
    ]
}

adapter = (
    TargetObjectWithNewValueAdapter()
)

request = (
    adapter.parse(
        source_data
    )
)

print("=" * 80)
print("REQUEST")
print(
    request.model_dump(
        mode="json"
    )
)
print("=" * 80)

resolver = WorkflowResolver()

workflow_definition = (
    resolver.resolve(
        request
    )
)
print("=" * 80)
print("WORKFLOW")
print(
    workflow_definition
        .model_dump(
            mode="json"
        )
)
print("=" * 80)

plan = workflow_plan_engine.process(
    request
)

print("=" * 80)
print("PLAN")
print(
    plan.model_dump(
        mode="json"
    )
)
print("=" * 80)

active_execution = (
    workflow_runtime.plan_to_active(
        plan
    )
)

print("=" * 80)
print("ACTIVE EXECUTION")

print(
    active_execution.model_dump(
        mode="json"
    )
)

print("=" * 80)

print("=" * 80)
print("BUILD JOB TEST")

jobs = []

for action in active_execution.actions:

    job = scheduler._build_job(
        active_execution=
            active_execution,

        action=
            action,
    )

    jobs.append(
        job
    )

    print(
        action.id,
        "=>",
        job.execute_at
    )

print("=" * 80)


for job in jobs:

    print("=" * 80)

    print(
        job.model_dump(
            mode="json"
        )
    )

print("=" * 80)