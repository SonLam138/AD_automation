from datetime import datetime
from typing import Any

from app.auto_engine.models.base import SourceAdapter
from app.auto_engine.models.request_models import (
    Request,
    RequestContext,
    RequestSource,
)
from app.auto_engine.models.request_type import RequestType
from app.auto_engine.models.source_types import SourceType


class EmployeeOnboardingApiAdapter(SourceAdapter):

    def parse(
        self,
        source_data: dict[str, Any],
    ) -> Request:
        source_request_id = source_data.get(
            "source_request_id"
        )
        if (
            not source_request_id
            or not source_request_id.strip()
        ):
            raise ValueError(
                "source_request_id is required"
            )

        employee_id = source_data.get(
            "employee_id"
        )
        if not employee_id or not employee_id.strip():
            raise ValueError(
                "employee_id is required"
            )

        # Temporary until Mail Platform starts sending is_onprem:
        # true -> newbie; false or missing -> newbie_365.
        is_onprem = True
        context = (
            RequestContext.NEWBIE
            if is_onprem
            else RequestContext.NEWBIE_365
        )

        business_data = {
            "source_request_id": source_request_id.strip(),
            "employee_id": employee_id.strip(),
            "first_name": source_data["first_name"],
            "last_name": source_data["last_name"],
            "full_name": source_data["full_name"],
            "sam_account_name": source_data["sam_account_name"],
            "display_name": (
                source_data.get("display_name")
                or source_data["full_name"]
            ),
            "target_ou_dn": source_data["target_ou_dn"],
            "title": source_data["title"],
            "department": source_data["department"],
            "description": source_data.get("description"),
            "dry_run": bool(source_data.get("dry_run", False)),
            "groups": source_data.get("groups", []),
            "user_principal_name": source_data.get(
                "user_principal_name"
            ),
            "license_sku_id": source_data.get(
                "license_sku_id"
            ),
            "disabled_plan_ids": source_data.get(
                "disabled_plan_ids",
                [],
            ),
            "start_date": datetime.now(),
        }

        return Request(
            request_type=RequestType.EMPLOYEE_ONBOARDING,
            context=context,
            source=RequestSource(
                source_type=SourceType.API,
                source_reference=source_request_id.strip(),
            ),
            business_data=business_data,
        )
