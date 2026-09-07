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

    member_of: list[str] = Field(
        default_factory=list
        )


class EmployeeOffboardingData(BaseModel):
    employee_id: str

    email: EmailStr

    reason: str

    effective_time: datetime | None = None

    start_date: datetime | None = None

    #end_date: datetime | None = None

    target_ou : Optional[str] = None

    target_object: TargetObject



class EmployeeOffboardingApiRequest(
    BaseModel
):

    employee_id: str

    email: EmailStr

    reason: str

    effective_time: Optional[str] = None

    start_date: Optional[str] = None

    #end_date: Optional[str] = None
    target_ou : Optional[str] = None