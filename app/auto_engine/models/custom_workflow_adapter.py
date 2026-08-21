
from app.auto_engine.resolver.action_code_resolver import resolve_action_code
from .request_type import (
    RequestType
)
from datetime import datetime

from .request_models import (
    Request,
    RequestContext,
    RequestSource,
)
from .source_types import (
    SourceType
)
from app.auto_engine.models.custom_workflow_model import CustomTargetObject, CustomWorkflowData
from app.auto_engine.resolver.object_resolver import (OBJECT_RESOLVERS)

OBJECT_RESOLVER_MAPPING = {

    "USER":
        "resolve_user",

    "COMPUTER":
        "resolve_computer",

    "GROUP":
        "resolve_group",

    "OU":
        "resolve_ou",
}


SUPPORTED_DATETIME_FORMATS = [
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S"
]
def normalize_datetime(
    value: str,
) -> datetime:

    value = value.strip()

    for fmt in SUPPORTED_DATETIME_FORMATS:

        try:
            return datetime.strptime(
                value,
                fmt
            )

        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {value}"
    )


class CustomWorkflowAdapter:

    def __init__(self):
        pass


    def get_object_map(
        self,
        objects: list
    ):

        return {
            obj["alias"]: obj
            for obj in objects
        }

    
    def normalize_start_date(
        self,
        workflow_context: dict
    ) -> datetime:

        steps = (
            workflow_context[
                "normalizedSteps"
            ]
        )

        if not steps:

            raise ValueError(
                "Workflow has no steps"
            )

        execute_times = []

        for step in steps:

            execute_time = (
                step.get(
                    "executeTime"
                )
            )

            if not execute_time:

                continue

            execute_times.append(
                normalize_datetime(
                    execute_time
                )
            )

        if not execute_times:

            raise ValueError(
                "Workflow has no execute time"
            )

        return min(
            execute_times
        )


    def build_normalized_steps(
        self,
        objects: list,
        steps: list
    ):

        object_map = self.get_object_map(
            objects
        )

        normalized_steps = []

        for index, step in enumerate(
            steps,
            start=1
        ):

            object_ref = step.get(
                "objectRef"
            )

            if not object_ref:

                raise ValueError(
                    f"Step {index}: "
                    f"objectRef is required"
                )

            obj = object_map.get(
                object_ref
            )

            if not obj:

                raise ValueError(
                    f"Step {index}: "
                    f"Object not found: "
                    f"{object_ref}"
                )

            action = step.get(
                "action"
            )

            if not action:

                raise ValueError(
                    f"Step {index}: "
                    f"action is required"
                )

            action_code = resolve_action_code(
                obj.get(
                    "objectType"
                ),
                action
            )

            if not action_code:

                raise ValueError(
                    f"Action mapping not found "
                    f"for {obj.get('objectType')} "
                    f"/ {action}"
                )

            execute_time = step.get(
                "executeTime"
            )

            if not execute_time:

                raise ValueError(
                    f"Step {index}: "
                    f"executeTime is required"
                )

            try:

                datetime.fromisoformat(
                    execute_time
                )

            except ValueError as exc:

                raise ValueError(
                    f"Step {index}: "
                    f"Invalid executeTime: "
                    f"{execute_time}"
                ) from exc

            normalized_steps.append(
                {
                    "stepNumber":
                        index,

                    "objectRef":
                        object_ref,

                    "objectType":
                        obj.get(
                            "objectType"
                        ),

                    "action":
                        action,

                    "actionCode":
                        action_code,

                    "executeTime":
                        execute_time,

                    "parameters":
                        step.get(
                            "parameters",
                            {}
                        )
                }
            )

        return normalized_steps

    def build_workflow_context(
        self,
        workflow_info: dict,
        objects: list,
        steps: list
    ):

        if not workflow_info:

            raise ValueError(
                "workflow_info is required"
            )

        if not objects:

            raise ValueError(
                "At least one object is required"
            )

        if not steps:

            raise ValueError(
                "At least one step is required"
            )

        object_catalog = self.get_object_map(
            objects
        )

        normalized_steps = (
            self.build_normalized_steps(
                objects,
                steps
            )
        )

        return {
            "workflowInfo":
                workflow_info,

            "objectCatalog":
                object_catalog,

            "normalizedSteps":
                normalized_steps
        }

    def group_steps_by_object(
        self,
        workflow_context: dict
    ):

        object_catalog = (
            workflow_context[
                "objectCatalog"
            ]
        )

        normalized_steps = (
            workflow_context[
                "normalizedSteps"
            ]
        )

        grouped = {}

        for step in normalized_steps:

            object_ref = (
                step["objectRef"]
            )

            if object_ref not in grouped:

                grouped[
                    object_ref
                ] = {
                    "object":
                        object_catalog[
                            object_ref
                        ],

                    "steps": []
                }

            grouped[
                object_ref
            ][
                "steps"
            ].append(step)

        return grouped

    def build_registry_templates(
        self,
        workflow_context: dict
    ):

        grouped = (
            self.group_steps_by_object(
                workflow_context
            )
        )

        templates = []

        for object_ref, group_data in grouped.items():

            object_context = {
                "workflowInfo":
                    workflow_context[
                        "workflowInfo"
                    ],

                "objectCatalog": {
                    object_ref:
                        group_data["object"]
                },

                "normalizedSteps":
                    group_data["steps"]
            }

            template = (
                self.build_registry_template(
                    object_context
                )
            )

            templates.append(
                template
            )

        return templates

    def build_registry_template(
        self,
        workflow_context: dict
    ):
        workflow_info = (
            workflow_context[
                "workflowInfo"
            ]
        )

        steps = (
            workflow_context[
                "normalizedSteps"
            ]
        )
        first_step = steps[0]
        object_ref = (
            first_step[
                "objectRef"
            ]
        )
        object_resolver = (
            OBJECT_RESOLVER_MAPPING[
                first_step[
                    "objectType"
                ]
            ]
        )

        template_context = (
            f"{workflow_info['context']}"
            f"_{object_ref}"
        )

        compiled_actions = []
        for step in steps:
            compiled_actions.append(
            {
                "id":
                    f"STEP_{step['stepNumber']:02d}",

                "action_code":
                    step[
                        "actionCode"
                    ],

                "display_name":
                    step[
                        "action"
                    ],

                "execution": {

                    "execute_time":
                        step[
                            "executeTime"
                        ],

                    "depends_on": [],

                    "retry_count":
                        3,

                    "continue_on_error":
                        False
                }
            }
            )
        return {

            "match": {

                "request_type":
                    RequestType.CUSTOM_WORKFLOW,

                "contexts": [
                    template_context
                ]
            },

            "workflow_id":
                workflow_info[
                    "workflowId"
                ],

            "workflow_name":
                workflow_info[
                    "workflowName"
                ],

            "object_resolver": object_resolver,
            "workflow_complete": False,

            "metadata": {

                "target_object_type":
                    first_step[
                    "objectType"
                    ],

                "schedule_mode":
                    "AT_EFFECTIVE_TIME",

                "trigger_field":
                    "start_date",

                "priority":
                    "NORMAL",

                "allow_retry":
                    True,

                "max_retry":
                    3
            },

            "actions":
                compiled_actions
        }

    def build_custom_target_object(
        self,
        resolved_object: dict
    ):

        object_type = (
            resolved_object.get(
                "object_type"
            )
        )

        if not object_type:

            raise ValueError(
                "Resolved object missing "
                "object_type"
            )

        dn = (
            resolved_object.get(
                "dn"
            )
            or
            resolved_object.get(
                "distinguished_name"
            )
        )

        if not dn:

            raise ValueError(
                "Resolved object missing DN"
            )

        excluded_fields = {
            "object_type",
            "dn",
            "distinguished_name"
        }

        clean_business_data = {
            key: value
            for key, value
            in resolved_object.items()
            if key not in excluded_fields
        }

        return CustomTargetObject(
            object_type=object_type,
            dn=dn,
            business_data=
                clean_business_data
        )




    

    def build_requests(
        self,
        workflow_context: dict,
        templates: list
    ):

        grouped = (
            self.group_steps_by_object(
                workflow_context
            )
        )

        workflow_info = (
            workflow_context[
                "workflowInfo"
            ]
        )

        normalized_steps = (
            workflow_context[
                "normalizedSteps"
            ]
        )

        if not normalized_steps:

            raise ValueError(
                "Workflow has no normalized steps"
            )

        workflow_start_date = min(
            step["executeTime"]
            for step in normalized_steps
        )

        template_by_context = {}

        for template in templates:

            contexts = (
                template
                .get(
                    "match",
                    {}
                )
                .get(
                    "contexts",
                    []
                )
            )

            for context in contexts:

                if context in template_by_context:

                    raise ValueError(
                        "Duplicate template context: "
                        f"{context}"
                    )

                template_by_context[
                    context
                ] = template

        requests = []

        for object_ref, group_data in (
            grouped.items()
        ):

            source_object = (
                group_data[
                    "object"
                ]
            )

            request_context = (
                f"{workflow_info['context']}"
                f"_{object_ref}"
            )

            template = (
                template_by_context.get(
                    request_context
                )
            )

            if not template:

                raise ValueError(
                    "Template not found for "
                    f"context: {request_context}"
                )

            resolver_name = (
                template.get(
                    "object_resolver"
                )
            )

            if not resolver_name:

                raise ValueError(
                    "Template missing "
                    f"object_resolver: "
                    f"{request_context}"
                )

            resolver_fn = (
                OBJECT_RESOLVERS.get(
                    resolver_name
                )
            )

            if not resolver_fn:

                raise ValueError(
                    "Object resolver not registered: "
                    f"{resolver_name}"
                )

            resolved_object = (
                resolver_fn(
                    source_object
                )
            )

            target_object = (
                self.build_custom_target_object(
                    resolved_object
                )
            )

            action_data = {}

            for step in group_data["steps"]:

                action_id = (
                    f"STEP_"
                    f"{step['stepNumber']:02d}"
                )

                action_data[
                    action_id
                ] = step.get(
                    "parameters",
                    {}
                )

            custom_workflow_data = (
                CustomWorkflowData(
                    start_date=
                        self.normalize_start_date(workflow_context),

                    target_object=
                        target_object,

                    action_data=
                        action_data
                )
            )

            request = Request(
                request_type=
                    RequestType
                    .CUSTOM_WORKFLOW,

                context=
                    request_context,

                source=RequestSource(
                    source_type=
                        SourceType.API,

                    source_reference=
                        workflow_info.get(
                            "workflowId"
                        )
                ),

                business_data=
                    custom_workflow_data
                    .model_dump(
                        mode="json"
                    )
            )

            requests.append(
                request
            )

        return requests

