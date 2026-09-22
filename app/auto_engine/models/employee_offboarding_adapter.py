import re
from datetime import datetime
from .base import SourceAdapter

from .request_models import (
    Request,
    RequestContext,
    RequestSource,
)

from .employee_offboarding import (
    EmployeeOffboardingData,
    TargetObject
)
from .request_type import (
    RequestType
)
from .source_types import (
    SourceType
)
from .source_model import (
    EmailRequestData)
from app.auto_engine.resolver.object_resolver import *

OFFBOARDING_CONTEXT_MAPPING = {
    "RESIGNED": [
        "nghỉ việc",
        "resigned",
    ],

    "LONG_LEAVE": [
        "chế độ",
        "thai sản",
    ],

}

OFFBOARDING_TARGET_OU_MAPPING = {
    "RESIGNED":
        "OU=Disabled Account, DC=automate, DC=com, DC=vn",

    "LONG_LEAVE":
        "OU=Nghi che do, DC=automate, DC=com, DC=vn",
}


SUPPORTED_DATETIME_FORMATS = [
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S"
]

def extract_ou_dn(
    distinguished_name: str,
) -> str:

    if not distinguished_name:
        return ""

    parts = (
        distinguished_name.split(",")
    )

    return ",".join(
        part
        for part in parts
        if not part.upper().startswith(
            "CN="
        )
    )

def normalize_datetime(
    value: str,
) -> datetime:

    value = value.strip()

    for fmt in SUPPORTED_DATETIME_FORMATS:

        try:
            return datetime.strptime(
                value,
                fmt
            )

        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {value}"
    )

def normalize_context(
    form_value: str,
) -> RequestContext:

    value = form_value.strip().lower()

    for context, keywords in (
        OFFBOARDING_CONTEXT_MAPPING.items()
    ):
        for keyword in keywords:

            if keyword in value:
                return context

    raise ValueError(
        f"Unsupported offboarding form: {form_value}"
    )

def normalize_target_ou(
    source_data: dict,
    context: RequestContext,
) -> str:

    return (
        OFFBOARDING_TARGET_OU_MAPPING
        .get(
            context,
            OFFBOARDING_TARGET_OU_MAPPING[
                "RESIGNED"
            ],
        )
    )


from datetime import datetime


def normalize_start_date(
    source_data: dict
) -> datetime:

    candidates = [
        "start_date",
        "effective_time",
        "effective_date",
        "ngay_hieu_luc",
        "ngay_bat_dau",
        "ngay_nghi_viec"
    ]

    for field in candidates:

        value = source_data.get(field)

        if value:
            return normalize_datetime(
                value
            )

    raise ValueError(
        "Start date not found"
    )


def normalize_end_date(
    source_data: dict
) -> datetime | None:

    candidates = [
        "end_date",
        "ngay_ket_thuc",
        "return_date"
    ]

    for field in candidates:

        value = source_data.get(field)

        if value:
            return normalize_datetime(
                value
            )

    return None

class EmployeeOffboardingApiAdapter(
    SourceAdapter
):

    def parse(
        self,
        source_data
    ) -> Request:

        reason = source_data.get(
            "reason"
        )

        if not reason:
            raise ValueError(
                "reason is required"
            )

        context = normalize_context(
            reason
        )
        target_ou = normalize_target_ou(
            source_data,
            context,
        )

        target_object = (
            resolve_user(
                source_data
            )
        )
        print(target_object)
        snapshot_data = {

            "request_context":
                reason,

            "employee_id":
                source_data[
                    "employee_id"
                ],

            "sam_account_name":
                target_object[
                    "sam_account_name"
                ],

            "snapshot_json": {

                "ou_dn":
                    extract_ou_dn(
                        target_object[
                            "dn"
                        ]
                    ),

                "groups":
                    target_object[
                        "member_of"
                    ]
            }
        }

        business_data = (
            EmployeeOffboardingData(
                employee_id=source_data["employee_id"],
                email=source_data["email"],
                start_date=normalize_start_date(source_data),
                is_emergency=bool(
                    source_data.get(
                        "is_emergency",
                        False,
                    )
                ),
                emergency_execute_at=(
                    normalize_datetime(
                        source_data[
                            "emergency_execute_at"
                        ]
                    )
                    if source_data.get(
                        "emergency_execute_at"
                    )
                    else None
                ),
                reason=reason,
                target_ou=target_ou,

                target_object=TargetObject(
                    object_type="user",

                    sam_account_name=
                        target_object[
                            "sam_account_name"
                        ],

                    email=
                        target_object[
                            "email"
                        ],

                    display_name=target_object["display_name"],

                    dn=
                        target_object[
                            "dn"
                        ],

                    is_remote_mailbox=
                        target_object.get(
                            "is_remote_mailbox",
                            False,
                        ),

                    member_of=
                        target_object.get(
                            "member_of",
                            []
                        ),
                )
            )
        )

        source_type = (
            source_data.get(
                "source_type"
            )
        )

        if source_type:

            source_type = (
                SourceType(
                    source_type.lower()
                )
            )

        else:

            source_type = (
                SourceType.API
            )

        return Request(

            request_type=
                RequestType
                .EMPLOYEE_OFFBOARDING,

            context=context,

            source=RequestSource(

                source_type=
                    source_type,

                source_reference=
                    source_data.get(
                        "source_reference"
                    )
            ),

            business_data=
                business_data.model_dump(
                    mode="json"
            ),

            snapshot_data=
                snapshot_data
        )

class EmployeeOffboardingUIAdapter(
    SourceAdapter
):

    def parse(self, source_data):

        form_value = source_data.get(
            "Hình thức"
        )

        if not form_value:
            raise ValueError(
                "Hình thức is required"
            )

        context = normalize_context(
            form_value
        )

        target_object = (
            resolve_user(
                source_data
            )
        )

        business_data = (
            EmployeeOffboardingData(
                employee_id=source_data["employee_id"],
                email=source_data["email"],
                start_date=normalize_start_date(source_data),
                reason=form_value,
                target_ou="Disabled Account",
        
                target_object=TargetObject(
                    object_type="user",
        
                    sam_account_name=
                        target_object[
                            "sam_account_name"
                        ],
        
                    email=
                        target_object[
                            "email"
                        ],
        
                    dn=
                        target_object[
                            "dn"
                        ],

                    is_remote_mailbox=
                        target_object.get(
                            "is_remote_mailbox",
                            False,
                        ),
                )
            )
        )
        
        return Request(
        
            request_type=
                RequestType
                .EMPLOYEE_OFFBOARDING,
        
            context=context,
        
            source=RequestSource(
                source_type=
                    SourceType.UI
            ),
        
            business_data=
                business_data.model_dump(
                    mode="json"
                )
        )

class EmployeeOffboardingEmailAdapter(
    SourceAdapter
):

    def parse(
        self,
        email_data: EmailRequestData,
    ) -> Request:

        body = email_data.body

        employee_id_match = re.search(
            r"Employee ID:\s*(.+)$",
            body,
            re.IGNORECASE | re.MULTILINE,
        )

        email_match = re.search(
            r"Email:\s*(.+)$",
            body,
            re.IGNORECASE | re.MULTILINE,
        )

        effective_time_match = re.search(
            r"Ngày hiệu lực:\s*(.+)$",
            body,
            re.IGNORECASE | re.MULTILINE,
        )

        form_match = re.search(
            r"Hình thức:\s*(.+)$",
            body,
            re.IGNORECASE | re.MULTILINE,
        )

        if not employee_id_match:
            raise ValueError(
                "Employee ID not found in email"
            )

        if not email_match:
            raise ValueError(
                "Email not found in email"
            )

        if not effective_time_match:
            raise ValueError(
                "Effective Time not found in email"
            )

        if not form_match:
            raise ValueError(
                "Hình thức not found in email"
            )

        form_value = form_match.group(1).strip()

        context = normalize_context(
            form_value
        )

        target_object = (
            resolve_user(
                email_data
            )
        )

        business_data = (
            EmployeeOffboardingData(
                employee_id=email_data["employee_id"],
                email=email_data["email"],
                start_date=normalize_start_date(email_data),
                reason=form_value,
                target_ou="Disabled Account",
        
                target_object=TargetObject(
                    object_type="user",
        
                    sam_account_name=
                        target_object[
                            "sam_account_name"
                        ],
        
                    email=
                        target_object[
                            "email"
                        ],
        
                    dn=
                        target_object[
                            "dn"
                        ],

                    is_remote_mailbox=
                        target_object.get(
                            "is_remote_mailbox",
                            False,
                        ),
                )
            )
        )


        print("CONTEXT =", context)

        return Request(
            request_type=RequestType.EMPLOYEE_OFFBOARDING,

            context=context,

            source=RequestSource(
                source_type=SourceType.EMAIL,
                source_reference=email_data.message_id,
            ),

            business_data=business_data.model_dump(
                mode="json"
            ),
        )