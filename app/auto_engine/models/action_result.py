from typing import Any, Dict

from pydantic import BaseModel, Field


class ActionResult(BaseModel):

    success: bool

    message: str = ""

    error: str | None = None

    output_data: Dict[str, Any] = Field(
        default_factory=dict
    )