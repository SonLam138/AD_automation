from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.auto_engine.models.workflow_definition import WorkflowAction


class ActiveExecutionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    JOB_CREATED = "JOB_CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ActiveExecution(BaseModel):
    # Snapshot từ ExecutionPlan
    request_id: str
    workflow_id: str
    execute_at: datetime
    actions: List[WorkflowAction]

    # Runtime progress
    status: ActiveExecutionStatus = (
        ActiveExecutionStatus.SCHEDULED
    )

    current_action_id: Optional[str] = None

    completed_action_ids: List[str] = Field(
        default_factory=list
    )

    failed_action_ids: List[str] = Field(
        default_factory=list
    )

    # Runtime metadata
    created_at: datetime = Field(
        default_factory=datetime.now
    )

    updated_at: datetime = Field(
        default_factory=datetime.now
    )
    
    is_scheduled: bool = False

    business_data: Dict[str, Any] = Field(
    default_factory=dict
    )