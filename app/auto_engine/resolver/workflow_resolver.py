from app.auto_engine.models.workflow_definition import (
    WorkflowDefinition
)

from app.auto_engine.resolver.workflow_registry import (
    WORKFLOW_REGISTRY
)
from copy import deepcopy

class WorkflowResolver:
    @staticmethod
    def _materialize_actions(
        actions: list,
        business_data: dict
    ):
        actions = deepcopy(
            actions
        )

        step_execute_times = {}

        for item in business_data.get(
            "step_execute_times",
            []
        ):
            print(type(item))
            print(item)

            step_execute_times[
                item["step_id"]
            ] = item["execute_at"]

        for action in actions:

            execute_time = (
                action.execution.execute_time
            )

            if execute_time != "UI_CUSTOM":
                continue

            execute_at = (
                step_execute_times.get(
                    action.id
                )
            )

            if execute_at is None:
                raise ValueError(
                    f"Missing execute time "
                    f"for step {action.id}"
                )

            action.execution.execute_time = (
                execute_at.isoformat()
                if hasattr(
                    execute_at,
                    "isoformat"
                )
                else str(
                    execute_at
                )
            )

        return actions

    
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

                workflow_definition = (
                    WorkflowDefinition(
                        **{
                            key: value
                            for key, value
                            in workflow_data.items()
                            if key != "match"
                        }
                    )
                )

                workflow_definition.actions = (
                    self._materialize_actions(
                        workflow_definition.actions,
                        request.business_data
                    )
                )

                return workflow_definition

        raise ValueError(
            f"Workflow not found: {key}"
        )