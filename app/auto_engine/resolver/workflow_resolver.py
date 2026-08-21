from app.auto_engine.models.workflow_definition import (
    WorkflowDefinition
)

from app.auto_engine.resolver.workflow_registry import (
    WORKFLOW_REGISTRY
)




class WorkflowResolver:

    def resolve(
        self,
        request
    ) -> WorkflowDefinition:

        key = (
            request.request_type,
            request.context
        )

        for workflow_data in WORKFLOW_REGISTRY:

            match = workflow_data["match"]
            print(
                "MATCH TYPE:",
                match["request_type"],
                type(match["request_type"])
            )

            print(
                "REQUEST TYPE:",
                request.request_type,
                type(request.request_type)
            )

            print(
                "MATCH CONTEXT:",
                match["contexts"]
            )

            print(
                "REQUEST CONTEXT:",
                request.context
            )

            if (
                match["request_type"]
                == request.request_type
                and request.context
                in match["contexts"]
            ):

                return WorkflowDefinition(
                    **{
                        key: value
                        for key, value
                        in workflow_data.items()
                        if key != "match"
                    }
                )

        raise ValueError(
            f"Workflow not found: {key}"
        )