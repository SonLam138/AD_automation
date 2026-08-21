from pydantic import BaseModel


class CustomWorkflowSaveRequest(BaseModel):

    workflowInfo: dict

    objects: list

    steps: list