from enum import Enum


class RequestType(str, Enum):
    EMPLOYEE_OFFBOARDING = "employee_offboarding"
    EMPLOYEE_ONBOARDING ="employee_onboarding"
    CUSTOM_WORKFLOW = "custom_workflow"
    TEMP_ACCESS_COMPUTER = ("temp_access_computer")
    TEMP_ACCESS_USER = ("temp_access_user")
    TEMP_OFFBOARDING = "temp_offboarding"
    DEPARTMENT_CHANGE = "department_change"