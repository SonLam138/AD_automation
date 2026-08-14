from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field
from enum import Enum

from .request_type import (
    RequestType
)

from .source_types import (
    SourceType
)

from .request_status import (
    RequestStatus
)


class RequestSource(BaseModel):
    source_type: SourceType

    source_reference: str | None = None



class RequestContext(str, Enum):
    RESIGNED = "RESIGNED"
    LONG_LEAVE = "LONG_LEAVE"

    

class Request(BaseModel):
    request_id: Optional[str] = None

    request_type: RequestType

    context: RequestContext

    source: RequestSource

    business_data: dict[str, Any]

    status: RequestStatus = (
        RequestStatus.NEW
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )