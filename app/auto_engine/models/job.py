from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Job(BaseModel):
    job_id: str

    request_id: str
    workflow_id: str

    action_id: str
    action_code: str
    display_name: str

    execute_at: datetime

    depends_on: List[str] = Field(
        default_factory=list
    )

    max_retry: int = 0

    continue_on_error: bool = False

    business_data: Dict[str, Any] = Field(
        default_factory=dict
    )

    status: JobStatus = JobStatus.PENDING

    retry_count: int = 0

    created_at: datetime = Field(
        default_factory=datetime.now
    )

    updated_at: datetime = Field(
        default_factory=datetime.now
    )

    started_at: datetime | None = None

    completed_at: datetime | None = None

    result_message: str | None = None

    error_message: str | None = None