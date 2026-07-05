from datetime import datetime
from pydantic import BaseModel


class AuditSessionStep(BaseModel):

    session_id: str

    step_name: str

    status: str

    started_at: datetime

    completed_at: datetime | None = None

    duration_ms: int | None = None

    error_code: str | None = None

    error_message: str | None = None
    
    details: dict | None = None