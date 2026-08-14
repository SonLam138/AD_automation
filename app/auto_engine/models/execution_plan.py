from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from app.auto_engine.models.workflow_definition import WorkflowAction


class ExecutionPlan(BaseModel):

    request_id: str

    workflow_id: str

    execute_at: datetime

    actions: List[WorkflowAction]

    business_data: dict = Field(efault_factory=dict)
