from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class TargetObject(
    BaseModel
):

    object_type: str

    sam_account_name: str

    display_name: str

    email: EmailStr

    dn: str

    is_remote_mailbox: bool = False

    member_of: list[str] = Field(
        default_factory=list
        )


class EmployeeOffboardingData(BaseModel):
    employee_id: str

    email: EmailStr

    reason: str

    #effective_time: datetime | None = None

    start_date: datetime | None = None

    is_emergency: bool = False

    emergency_execute_at: datetime | None = None

    #end_date: datetime | None = None

    target_ou : Optional[str] = None

    target_object: TargetObject



class EmployeeOffboardingApiRequest(
    BaseModel
):

    employee_id: str

    email: EmailStr

    reason: str

    subject: str | None = None

    sender: str | None = None

    start_date: Optional[str] = None

    effective_time: Optional[str] = None

    is_emergency: bool = False

    emergency_execute_at: Optional[str] = None

    target_ou : Optional[str] = None

    source_type: str | None = None

    source_reference: str | None = None