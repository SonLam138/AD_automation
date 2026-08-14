from enum import Enum


class RequestStatus(str, Enum):
    NEW = "new"

    VALIDATED = "validated"

    REJECTED = "rejected"

    PROCESSING = "processing"

    COMPLETED = "completed"

    FAILED = "failed"