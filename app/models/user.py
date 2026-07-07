from pydantic import BaseModel, Field
from typing import Optional

class CreateUserRequest(BaseModel):

    #request_id: str

    employee_id: str

    first_name: str

    last_name: str

    full_name: str

    display_name: str | None = None

    sam_account_name: str
    
    password: str

    target_ou_dn: str

    title: str

    department: str

    description: str | None = None

    edited_by_approver: bool = False

    dry_run: bool = True
    
    groups: list[str] = Field(
        default_factory=list
    )
