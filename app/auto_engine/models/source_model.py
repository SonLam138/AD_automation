from pydantic import BaseModel


class EmailRequestData(BaseModel):

    subject: str

    body: str

    sender: str | None = None

    message_id: str | None = None