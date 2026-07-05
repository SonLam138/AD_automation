from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.auth.rbac import require_role

from app.models.user import (
    CreateUserRequest
)

from app.adapters.ldap_adapter import (
    LDAPAdapter
)

from app.config import *

router = APIRouter()

ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)

def get_current_user_value(
    current_user,
    key,
    default=None
):
    if current_user is None:
        return default

    if isinstance(
        current_user,
        dict
    ):
        return current_user.get(
            key,
            default
        )

    return getattr(
        current_user,
        key,
        default
    )

@router.post("/new")
def new_onboarding(
    request: CreateUserRequest,

    current_user=Depends(
        require_role(
            [
                "ad.operator",
                "ad.admin"
            ]
        )
    )
):
    
    approved_by = (
            get_current_user_value(
                current_user,
                "username"
            )
            or
            get_current_user_value(
                current_user,
                "sub"
            )
            or
            get_current_user_value(
                current_user,
                "email"
            )
        )

    approved_name = (
        get_current_user_value(
            current_user,
            "full_name"
        )
        or
        get_current_user_value(
            current_user,
            "name"
        )
        or
        approved_by
    )

    
    result = ldap.create_user(
        request=request,
        approved_by=approved_by,
        approved_name=approved_name,
        approval_type="MANUAL"
    )

    if not result["success"]:

        raise HTTPException(
            status_code=500,
            detail={
                "session_id":
                    result["session_id"],

                "message":
                    "Onboarding failed",

                "error":
                    result.get("error")
            }
        )
    return {

        "success": True,

        "session_id":
            result["session_id"],

        "capability":
            "new_onboarding",

        "account":
            result["actual_account"],

        "display_name":
            result["DisplayName"],

        "status":
            "completed"
    }