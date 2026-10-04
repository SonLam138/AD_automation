from pydantic import BaseModel
from datetime import datetime


class PendingRequest(BaseModel):

    request_id: str

    status: str

    created_at: datetime

    hr_input: dict

    resolved_result: dict


class RejectRequest(BaseModel):

    request_id: str