from .wf_with_newvalue import TargetObjectWithNewValue, WFDataWithNewValue, StepExecuteTime, StepNewValue
from .request_type import (
    RequestType
)
from .source_types import (
    SourceType
)
from .base import SourceAdapter
from .request_models import Request, RequestSource
from app.auto_engine.resolver.object_resolver import resolve_computer, resolve_user
from datetime import datetime

SUPPORTED_DATETIME_FORMATS = [
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S",

    # React datetime + toISOString()
    "%Y-%m-%dT%H:%M:%S.%fZ",
]
def normalize_datetime(
    value: str,
) -> datetime:

    value = value.strip()

    # ISO chuẩn browser
    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except (
        ValueError,
        TypeError,
    ):
        pass

    for fmt in (
        SUPPORTED_DATETIME_FORMATS
    ):

        try:

            return datetime.strptime(
                value,
                fmt
            )

        except ValueError:

            continue

    raise ValueError(
        f"Invalid datetime format: {value}"
    )

def extract_ou_from_dn(
    distinguished_name: str
) -> str:

    if "OU=" not in distinguished_name:
        return ""

    parts = distinguished_name.split(",")

    return ",".join(
        part
        for part in parts
        if part.startswith("OU=")
        or part.startswith("DC=")
    )

def build_target_object(
    target_object: dict
) -> TargetObjectWithNewValue:

    return (
        TargetObjectWithNewValue(

            object_type=
                target_object[
                    "object_type"
                ],

            sam_account_name=
                target_object.get(
                    "sam_account_name"
                ),

            computer_name=
                target_object.get(
                    "computer_name"
                ),

            dn=
                target_object.get(
                    "dn"
                )
        )
    )



def normalize_datetime_field(
    source_data: dict,
    field_name: str,
) -> datetime:

    value = source_data.get(
        field_name
    )

    if not value:
        raise ValueError(
            f"{field_name} is required"
        )

    if isinstance(
        value,
        datetime,
    ):
        return value

    try:

        return normalize_datetime(
            str(value)
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise ValueError(
            f"Invalid {field_name} format"
        ) from exc

def normalize_start_date(
    source_data: dict
) -> datetime | None:

    value = source_data.get(
        "start_date"
    )

    if not value:
        return None

    if isinstance(
        value,
        datetime
    ):
        return value

    try:

        return normalize_datetime(
            str(value)
        )

    except ValueError as exc:

        raise ValueError(
            "Invalid start_date format"
        ) from exc


class TargetObjectWithNewValueAdapter(
    SourceAdapter
):

    def parse(
        self,
        source_data
    ) -> Request:

        # =========================
        # COMPUTER
        # =========================

        request_type = (
            RequestType(
                source_data[
                    "request_type"
                ]
            )
        )

        if (
            request_type
            ==
            RequestType
            .TEMP_ACCESS_COMPUTER
        ):

            target_object = (
                resolve_computer(
                    source_data
                )
            )
           
        # =========================
        # USER
        # =========================

        elif (
            request_type
            ==
            RequestType
            .TEMP_ACCESS_USER
        ):

            target_object = (
                resolve_user(
                    source_data
                )
            )

        else:

            raise ValueError(
                "Unsupported object type"
            )

        step_execute_times = []
        for item in source_data.get(
            "step_execute_times",
            []
        ):
            step_execute_times.append(
                StepExecuteTime(
                    step_id=
                        item["step_id"],

                    execute_at=
                        normalize_datetime_field(
                            item,
                            "execute_at"
                        )
                )
            )
         

        step_new_values = []

        for item in source_data.get(
            "step_new_values",
            []
        ):
            step_new_values.append(
                StepNewValue(
                    step_id=
                        item[
                            "step_id"
                        ],

                    parameter_name=
                        item[
                            "parameter_name"
                        ],

                    new_value=
                        item[
                            "new_value"
                        ],
                )
            )


        business_data = (
            WFDataWithNewValue(
                start_date=
                    normalize_start_date(
                        source_data
                    ),

                step_execute_times = step_execute_times,

                step_new_values = step_new_values,

                target_object=
                    build_target_object(
                        target_object
                    )
            )
        )

        return Request(

            request_type=
                request_type,

            context=
                source_data[
                    "context"
                ],

            source=
                RequestSource(
                    source_type=
                        SourceType.UI
                ),

            business_data=
                business_data.model_dump(
                    mode="json"
                )
        )
