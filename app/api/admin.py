from fastapi import APIRouter
from fastapi import Depends

from app.auth.rbac import require_group

router = APIRouter()


@router.get("/health")
def health():

    return {
        "status": "ok"
    }


@router.get("/admin-only")
def admin_only(

    current_user = Depends(
        require_group(
            ["Administrators"]
        )
    )
):

    return {
        "message": "Welcome admin",
        "user": current_user["sub"]
    }