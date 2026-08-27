from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

class StepExecuteTime(
    BaseModel
):
    step_id: str

    execute_at: datetime

class StepNewValue(
    BaseModel
):
    step_id: str

    parameter_name: str

    new_value: Any


class TargetObjectWithNewValue(
    BaseModel
):
    object_type: str

    sam_account_name: str | None = None

    computer_name: str | None = None

    dn: str | None = None



class WFDataWithNewValue(
    BaseModel
):
    start_date: datetime | None = None

    step_execute_times: list[
        StepExecuteTime
    ] = Field(
        default_factory=list
    )

    step_new_values: list[
        StepNewValue
        ] = Field(
        default_factory=list
    )

    target_object: TargetObjectWithNewValue


class TempAccessComputerRequest(
    BaseModel
):
    computer_name: str

    start_date: str | None = None

    step_execute_times: list[
        StepExecuteTime
    ] = Field(
        default_factory=list
    )

    step_new_values: list[
        StepNewValue
    ] = Field(
        default_factory=list
    )


class TempAccessUserRequest(
    BaseModel
):
    sam_account_name: str

    start_date: str | None = None

    step_execute_times: list[
        StepExecuteTime
    ] = Field(
        default_factory=list
    )

    step_new_values: list[
        StepNewValue
    ] = Field(
        default_factory=list
    )

class TempResolveObjectRequest(
    BaseModel
):
    object_type: str

    keyword: str

    limit: int = 100