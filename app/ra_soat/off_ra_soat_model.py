from dataclasses import dataclass

from typing import Optional


@dataclass
class RaSoatOffboardingSourceUser:
    employee_id: str
    full_name: str
    effective_time: str

    email: str
    username: str

@dataclass
class RelatedAccountSearchResult:
    search_key: str

    found: bool

    sam_account_name: Optional[str] = None

    email: Optional[str] = None

    is_disabled: Optional[bool] = None