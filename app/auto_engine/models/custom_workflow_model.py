from pydantic import BaseModel
from pydantic import Field
from datetime import datetime

class CustomTargetObject(
    BaseModel
):

    object_type: str

    dn: str

    business_data: dict = (
        Field(
            default_factory=dict
        )
    )


class CustomWorkflowData(
    BaseModel
):

    start_date: datetime

    target_object: CustomTargetObject

    action_data: dict[
        str,
        dict
    ] = Field(
        default_factory=dict
    )