from pydantic import BaseModel, ConfigDict, Field
from pydantic import model_validator
from typing import Literal


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

class RestoreGroupsRequest(BaseModel):
    sam_account_name: str
    group_dns: list[str]


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


class CreateAdUserRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    sam_account_name: str
    password: str
    target_ou_dn: str
    title: str
    department: str
    display_name: str | None = None
    description: str | None = None
    edited_by_approver: bool = False
    dry_run: bool = True
    groups: list[str] = Field(default_factory=list)


class CreateGroupRequest(BaseModel):
    group_name: str
    target_ou_dn: str
    description: str | None = None


class IntegrationGroupMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["user", "computer", "group"] = "user"
    sam_account_name: str | None = Field(default=None, min_length=1)
    computer_name: str | None = Field(default=None, min_length=1)
    group_name: str | None = Field(default=None, min_length=1)
    member_group_email: str | None = Field(
        default=None,
        min_length=1,
    )
    member_group_ou: str | None = Field(
        default=None,
        min_length=1,
    )
    target_group: str | None = Field(default=None, min_length=1)
    target_group_email: str | None = Field(
        default=None,
        min_length=1,
    )
    target_group_ou: str | None = Field(
        default=None,
        min_length=1,
    )

    @model_validator(mode="after")
    def require_group_identifier(self):
        if not self.target_group and not self.target_group_email:
            raise ValueError(
                "target_group or target_group_email is required"
            )

        identifiers = {
            "user": self.sam_account_name,
            "computer": self.computer_name,
            "group": self.group_name or self.member_group_email,
        }

        if not identifiers[self.object_type]:
            raise ValueError(
                f"{self.object_type} member identifier is required"
            )

        if any(
            value
            for key, value in identifiers.items()
            if key != self.object_type
        ):
            raise ValueError(
                "Only the identifier matching object_type may be provided"
            )

        if (
            self.object_type != "group"
            and (
                self.member_group_email
                or self.member_group_ou
            )
        ):
            raise ValueError(
                "member_group_email and member_group_ou "
                "are only valid for group members"
            )

        return self


class IntegrationMoveToOuRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    object_type: Literal["user", "computer", "group"]
    target_ou: str = Field(min_length=1)
    target_ou_parent: str | None = Field(
        default=None,
        min_length=1,
    )
    sam_account_name: str | None = Field(default=None, min_length=1)
    computer_name: str | None = Field(default=None, min_length=1)
    group_name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_move_target(self):
        identifiers = {
            "user": self.sam_account_name,
            "computer": self.computer_name,
            "group": self.group_name,
        }

        if not identifiers[self.object_type]:
            raise ValueError(
                f"{self.object_type} identifier is required"
            )

        if any(
            value
            for key, value in identifiers.items()
            if key != self.object_type
        ):
            raise ValueError(
                "Only the identifier matching object_type may be provided"
            )

        return self