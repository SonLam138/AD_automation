from pydantic import BaseModel
from datetime import datetime

from typing import Optional


class SessionRequested(BaseModel):

    employee_id: str | None = None
    
    #password_set: bool | None = None

    #enabled: bool | None = None

    #must_change_password: bool | None = None

    first_name: str | None = None

    last_name: str | None = None

    full_name: str | None = None

    department: str | None = None

    title: str | None = None

    account: str | None = None

    display_name: str | None = None

    ou: str | None = None

class SessionActual(BaseModel):

    account: str | None = None

    display_name: str | None = None

    user_dn: str | None = None

    ou_dn: str | None = None

class AuditSessionContext(BaseModel):

    schema_version: str

    session_id: str

    event_category: str

    event_type: str

    source_type: str

    source_id: str | None = None

    capability: str

    status: str

    started_at: datetime

    completed_at: datetime | None = None

    duration_ms: int | None = None

    requested: SessionRequested

    actual: SessionActual

    failure_stage: str | None = None

    failure_code: str | None = None

    failure_reason: str | None = None
    
    # =====================================================
    # Approval Information
    # =====================================================
    approved_by: Optional[str] = None

    approved_name: Optional[str] = None

    edited_by_approver: bool = False

    approval_type: Optional[str] = None

    approval_time: Optional[datetime] = None
