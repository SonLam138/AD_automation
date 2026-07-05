from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter

from app.models.hr_request import HRRequest
from app.models.pending_request import PendingRequest
from app.storage.pending_requests import add_pending_request

router = router = APIRouter()

@router.post("/request")
def fake_resolve_onboarding(
    request: HRRequest
):

    request_id = (
        f"REQ-{uuid4().hex[:8].upper()}"
    )

    resolved_result = {

        "sam_account_name":
            "nguyentt",

        "display_name":
            "Truong Thao Nguyen (K.KHCN-SGN)",

        "target_ou_dn":
            "OU=HO,DC=Automate,DC=com,DC=vn",

        "groups": [
            "khcn.saigon"
        ]
    }
    pending_request = PendingRequest(

    request_id=request_id,

    status="PENDING",

    created_at=datetime.utcnow(),

    hr_input=request.model_dump(),

    resolved_result=resolved_result
)
    add_pending_request(
        pending_request.model_dump(
            mode="json"
        )
    )