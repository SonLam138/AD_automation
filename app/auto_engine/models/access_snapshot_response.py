from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AccessSnapshotResponse(BaseModel):
    success: bool

    request_id: str
    request_context: str

    employee_id: str
    sam_account_name: str

    captured_at: datetime

    user_status: str

    ou_dn: Optional[str]

    groups: List[str]