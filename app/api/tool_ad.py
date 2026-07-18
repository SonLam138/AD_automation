from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.auth.rbac import require_group

from app.models.ad_tool import (
    DisableUserRequest,
    AddGroupRequest,
    RemoveGroupRequest,
    MoveUserRequest
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

@router.post("/disable-user")
def disable_user(
    request: DisableUserRequest,

    current_user=Depends(
        require_group(
            [
                "ad_dis_user"
            ]
        )
    )
):

    try:

        print(
            "LDAP CONNECTED =",
            ldap.connection.bound
        )

        result = ldap.disable_user(
            request.sam_account_name
        )

        return result

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )
    
@router.post("/add-group")
def add_group(
    request: AddGroupRequest,

    current_user=Depends(
        require_group(
            [
                "ad_group_member"
            ]
        )
    )
):

    return ldap.add_group_member(
        request.sam_account_name,
        request.group_name
    )

@router.post("/remove-group")
def remove_group(
    request: RemoveGroupRequest,

    current_user=Depends(
        require_group(
            [
                "ad_group_member"
            ]
        )
    )
):

    return ldap.remove_group_member(
        request.sam_account_name,
        request.group_name
    )

@router.post("/move-user")
def move_user(
    request: MoveUserRequest,

    current_user=Depends(
        require_group(
            [
                "ad_move_ou"
            ]
        )
    )
):

    return ldap.move_user_to_ou(
        request.sam_account_name,
        request.target_ou_dn
    )