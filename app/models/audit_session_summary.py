from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditSessionSummary(BaseModel):
    session_id: str

    capability: str

    result: str

    summary_category: str

    execution_time_ms: int

    generated_at: datetime

    business_summary: dict

    technical_summary: dict

    error_summary: Optional[dict]
    
    # =====================================================
    # Approval Information
    # =====================================================
    approved_by: Optional[str] = None

    approved_name: Optional[str] = None

    approval_type: Optional[str] = None

    approval_time: Optional[datetime] = None
