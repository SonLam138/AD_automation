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

    "SUSPENDED": [
        "kỷ luật",
        "đình chỉ",
    ],
}


SUPPORTED_DATETIME_FORMATS = [
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S"
]

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

        target_object = (
            resolve_user(
                source_data
            )
        )
        print("=" * 80)
        print(target_object)
        print("=" * 80)

        business_data = (
            EmployeeOffboardingData(
                employee_id=source_data["employee_id"],
                email=source_data["email"],
                start_date=normalize_start_date(source_data),
                reason=reason,
                target_ou="OU=Disabled Account,DC=automate,DC=com,DC=vn",

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
                )
            )
        )
        print("=" * 80)
        print("BUSINESS DATA")
        print(
            business_data.model_dump(
                mode="json"
            )
        )
        print("=" * 80)

        return Request(

            request_type=
                RequestType
                .EMPLOYEE_OFFBOARDING,

            context=context,

            source=RequestSource(
                source_type=
                    SourceType.API
            ),

            business_data=
                business_data.model_dump(
                    mode="json"
                )
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