from pydantic import BaseModel


class HRRequest(BaseModel):

    employee_id: str

    full_name: str

    birth_date: str

    title: str

    position: str

    department: str

    division: str