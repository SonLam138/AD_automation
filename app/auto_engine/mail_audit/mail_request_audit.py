from dataclasses import dataclass

from typing import Optional


@dataclass
class MailRequestAudit:

    id: Optional[int]

    request_id: str

    workflow_id: str

    request_type: str

    reason: str

    employee_id: str

    email: str

    source_reference: Optional[str]

    sender: Optional[str]

    subject: Optional[str]

    is_emergency: bool

    created_time: str