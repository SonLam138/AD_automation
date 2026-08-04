from pydantic import BaseModel


class DisableUserRequest(BaseModel):
    sam_account_name: str

class AddGroupRequest(BaseModel):
    sam_account_name: str
    group_name: str


class RemoveGroupRequest(BaseModel):
    sam_account_name: str
    group_name: str

class MoveUserRequest(BaseModel):
    sam_account_name: str
    target_ou_dn: str


from pydantic import BaseModel

class AssistantMessageRequest(
    BaseModel
):
    message: str


class DisableComputerRequest(
    BaseModel
):
    computer_name: str

class VerifySecretRequest(BaseModel):
    secret: str

class UpdateUserDisplayNameRequest(
    BaseModel
):
    sam_account_name: str

    new_value: str

class DetectionFeedbackRequest(BaseModel):
    event_id: str
    feedback: str