from enum import Enum


class RequestType(str, Enum):
    EMPLOYEE_OFFBOARDING = "employee_offboarding"
    CUSTOM_WORKFLOW = "custom_workflow"
    TEMP_ACCESS_COMPUTER = ("temp_access_computer")
    TEMP_ACCESS_USER = ("temp_access_user")