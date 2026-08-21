from pprint import pprint

from app.auto_engine.models.custom_workflow_adapter import (
    CustomWorkflowAdapter
)
import json
from app.auto_engine.models.request_type import (
    RequestType
)
from app.auto_engine.models.workflow_definition import (
    WorkflowDefinition
)

workflow_info = {
    "workflowId":
        "WF_1787159331321",

    "workflowName":
        "Disable User And Computer",

    "context":
        "CUSTOM_WF_1787159331321"
}


objects = [
    {
        "alias": "VENDER_A",

        "objectType": "USER",

        "employee_id":
            "",

        "email":
            "ad.auto1@automate.com.vn"
    },

    {
        "alias": "MAY TINH_A",

        "objectType": "COMPUTER",

        "computer_name":
            "Client-01"
    }
]


steps = [

    {
        "objectRef":
            "VENDER_A",

        "action":
            "DISABLE",

        "executeTime":"2026-08-20T11:05",

        "dependsOn":
            "",

        "parameters":
            {}
    },

    {
        "objectRef":
            "MAY TINH_A",

        "action":
            "DISABLE",

        "executeTime":
            "2026-08-20T12:05",

        "dependsOn":
            "",

        "parameters":
            {}
    },
    {
            "objectRef":
                "VENDER_A",
    
            "action":
                "MOVE",
    
            "executeTime":"2026-08-29T11:05",
    
            "dependsOn":
                "",
    
            "parameters":
                {}
    },
    {
        "objectRef":
            "MAY TINH_A",
    
        "action":
            "MOVE",
    
        "executeTime":
            "2026-08-28T12:05",
    
        "dependsOn":
            "",
    
        "parameters":
            {}
    }

]


adapter = (
    CustomWorkflowAdapter()
)


workflow_context = (
    adapter.build_workflow_context(
        workflow_info,
        objects,
        steps
    )
)

print("\n=== WORKFLOW CONTEXT ===\n")

pprint(
    workflow_context,
    width=120
)

grouped = (
    adapter.group_steps_by_object(
        workflow_context
    )
)


print(
    json.dumps(
        grouped,
        indent=2
    )
)

templates = (
    adapter.build_registry_templates(
        workflow_context
    )
)
print(
    f"Templates Count: {len(templates)}"
)
import json

print(
    json.dumps(
        templates,
        indent=2
    )
)


template = templates[0]

workflow_definition = (
    WorkflowDefinition(
        **{
            k: v
            for k, v in template.items()
            if k != "match"
        }
    )
)

print("\n=== WORKFLOW DEFINITION ===")
print(workflow_definition)

print("\n=== ACTIONS ===")

for action in workflow_definition.actions:

    print(
        f"Action Code: "
        f"{action.action_code}"
    )

    print(
        f"Execute Time: "
        f"{action.execution.execute_time}"
    )

    print(
        f"Depends On: "
        f"{action.execution.depends_on}"
    )

    print("-----")




templates = (
    adapter.build_registry_templates(
        workflow_context
    )
)

requests = (
    adapter.build_requests(
        workflow_context,
        templates
    )
)

print("\n=== REQUESTS ===")

for request in requests:

    print("=" * 80)

    print(
        "CONTEXT:"
    )

    print(
        request.context
    )

    print()

    print(
        "BUSINESS DATA:"
    )

    print(
        request.business_data
    )