from pydantic import BaseModel


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

    dry_run: bool = False