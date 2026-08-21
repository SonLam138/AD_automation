from pydantic import BaseModel
from typing import List


class WorkflowExecution(BaseModel):
    depends_on: List[str] = []
    delay_minutes: int = 0
    execute_time: str | None = None
    retry_count: int = 3
    continue_on_error: bool = False


class WorkflowAction(BaseModel):
    id: str
    action_code: str
    display_name: str
    execution: WorkflowExecution


class WorkflowDefinition(BaseModel):
    workflow_name: str

    workflow_id: str

    metadata: dict

    actions: List[WorkflowAction]