# app/models/integration_token_request.py

from pydantic import BaseModel


class IntegrationTokenRequest(
    BaseModel
):

    client_id: str

    client_secret: str