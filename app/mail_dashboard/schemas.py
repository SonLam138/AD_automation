from datetime import (
    datetime,
    timezone,
)
from typing import (
    Literal,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


MailProcessingStateValue = Literal[
    "PENDING",
    "PROCESSING",
    "RETRY_PENDING",
    "SUCCESS",
    "BUSINESS_REJECTED",
    "INVALID_REQUEST",
    "UNSUPPORTED_REQUEST",
    "RETRY_EXHAUSTED",
]


class MailDashboardSnapshot(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=False,
    )

    schema_version: Literal[1]
    source_system: Literal["mail-platform"]
    mailbox: str = Field(
        min_length=1,
    )
    source_mail_id: str = Field(
        min_length=1,
    )
    subject: str
    received_at: datetime | None = None
    processing_state: MailProcessingStateValue
    state_changed_at: datetime

    @field_validator("mailbox")
    @classmethod
    def normalize_mailbox(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("mailbox must not be blank")
        return normalized

    @field_validator("source_mail_id")
    @classmethod
    def source_mail_id_must_not_be_blank(
        cls,
        value: str,
    ) -> str:
        if not value.strip():
            raise ValueError("source_mail_id must not be blank")
        return value

    @field_validator(
        "received_at",
        "state_changed_at",
        mode="before",
    )
    @classmethod
    def timestamp_must_be_a_string(
        cls,
        value: object,
    ) -> object:
        if value is not None and not isinstance(value, str):
            raise ValueError("timestamps must use RFC 3339 strings")
        return value

    @field_validator("received_at", "state_changed_at")
    @classmethod
    def normalize_timestamp(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must include a timezone")
        return value.astimezone(timezone.utc)

    def to_record_values(self) -> dict[str, str | None]:
        return {
            "source_system": self.source_system,
            "mailbox": self.mailbox,
            "source_mail_id": self.source_mail_id,
            "subject": self.subject,
            "received_at": (
                self.received_at.isoformat(
                    timespec="microseconds",
                )
                if self.received_at
                else None
            ),
            "processing_state": self.processing_state,
            "state_changed_at": self.state_changed_at.isoformat(
                timespec="microseconds",
            ),
        }


class MailDashboardSnapshotResponse(BaseModel):
    status: Literal[
        "created",
        "updated",
        "unchanged",
        "stale",
    ]
    changed: bool


class MailDashboardFailureSummary(BaseModel):
    mailbox: str
    received_at: datetime | None
    subject: str
    processing_state: MailProcessingStateValue


class MailDashboardSummaryResponse(BaseModel):
    total_mail: int
    mail_last_24h: int
    failed_mail: int
    successful_mail: int
    recent_failed_mail: list[MailDashboardFailureSummary]
