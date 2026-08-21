from enum import Enum


class RequestType(str, Enum):
    EMPLOYEE_OFFBOARDING = "employee_offboarding"
    CUSTOM_WORKFLOW = "custom_workflow"