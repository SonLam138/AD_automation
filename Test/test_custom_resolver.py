from app.auto_engine.models.request_models import (
    Request,
    RequestSource
)

from app.auto_engine.models.request_type import (
    RequestType
)

from app.auto_engine.models.source_types import (
    SourceType
)

from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver
)

request = Request(

    request_type=
        RequestType.CUSTOM_WORKFLOW,

    context=
        "CUSTOM_WF_1787284539271_Vender_A",

    source=RequestSource(
        source_type=
            SourceType.UI
    ),

    business_data={}
)

resolver = WorkflowResolver()

workflow = (
    resolver.resolve(
        request
    )
)

print("=" * 80)

print(
    workflow.workflow_id
)

print(
    workflow.workflow_name
)

for action in workflow.actions:

    print(
        action.action_code
    )

    print(
        action.execution.execute_time
    )

    