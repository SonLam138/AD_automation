from app.auto_engine.models.request_type import (
    RequestType
)

WORKFLOW_REGISTRY = [
    {
        "match": {
            "request_type": RequestType.EMPLOYEE_OFFBOARDING,
            "contexts": [
                "RESIGNED"
            ]
        },

        "workflow_id": "OFFBOARDING_RESIGNED",

        "workflow_name": "Employee Offboarding - Resigned",
        "object_resolver": "resolve_user",

        "metadata": {

            "target_object_type": "USER",

            "schedule_mode": "AT_EFFECTIVE_TIME",

            "trigger_field": "start_date",

            "priority": "NORMAL",

            "allow_retry": True,

            "max_retry": 3
        },

        "actions": [

            {
                "id": "STEP_01",

                "action_code": "disable_user",

                "display_name": "Disable User",

                "execution": {
                    "depends_on": [],
                    "delay_minutes": 0,
                    "retry_count": 3,
                    "continue_on_error": False
                }
            },

            {
                "id": "STEP_02",

                "action_code": "move_disabled_ou",

                "display_name": "Move To Disabled OU",

                "execution": {
                    "depends_on": ["STEP_01"],
                    "delay_minutes": 30,
                    "retry_count": 3,
                    "continue_on_error": False
                }
            }
        
        ]
    }
]