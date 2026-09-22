from dataclasses import dataclass

from app.auto_engine.sqlite.mail_request_audit_record import (
    MailRequestAuditRecord,
)
from datetime import datetime


@dataclass
class MailRequestReport:

    total_requests: int

    emergency_requests: int

    workflow_summary: list[dict]

    reason_summary: list[dict]

    period_start: datetime

    period_end: datetime

    details: list[
        MailRequestAuditRecord
    ]