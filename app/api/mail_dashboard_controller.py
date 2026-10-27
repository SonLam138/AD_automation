from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.auth.integration_authorization import (
    require_integration_endpoint,
)
from app.auth.rbac import (
    require_group,
)
from app.mail_dashboard.repository import (
    MailDashboardSnapshotConflict,
)
from app.mail_dashboard.schemas import (
    MailDashboardSnapshot,
    MailDashboardSnapshotResponse,
    MailDashboardSummaryResponse,
)
from app.mail_dashboard.service import (
    MailDashboardService,
)


router = APIRouter()
mail_dashboard_service = MailDashboardService()


@router.post(
    "/snapshots",
    response_model=MailDashboardSnapshotResponse,
)
def receive_mail_snapshot(
    snapshot: MailDashboardSnapshot,
    claims=Depends(
        require_integration_endpoint(
            "mail_dashboard_snapshot",
        )
    ),
):
    try:
        status = mail_dashboard_service.upsert_snapshot(snapshot)
    except MailDashboardSnapshotConflict as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex),
        ) from ex

    return {
        "status": status,
        "changed": status in {"created", "updated"},
    }


@router.get(
    "/summary",
    response_model=MailDashboardSummaryResponse,
)
def get_mail_dashboard_summary(
    current_user=Depends(
        require_group(["ad_login"])
    ),
):
    return mail_dashboard_service.get_summary()
