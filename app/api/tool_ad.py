from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.auth.rbac import require_group

from app.models.ad_tool import (
    DisableUserRequest,
    AddGroupRequest,
    RemoveGroupRequest,
    MoveUserRequest,
    VerifySecretRequest,
    DisableComputerRequest,
    UpdateUserDisplayNameRequest
)
from app.agent.execution_response import (
    generate_execution_response
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

        result = ldap.disable_user(
            request.sam_account_name
        )



        execution_contract = {
            "state": "ACTION_SUCCESS",
            "action": "disable_user",
            "proposed_action_payload": {
                "sam_account_name":
                    request.sam_account_name
            },
            "execution_result": result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

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
    try:

        result = ldap.add_group_member(
            request.sam_account_name,
	    request.group_name
        )

        execution_contract = {
            "state": "ACTION_SUCCESS",
            "action": "add_group_member",
            "proposed_action_payload": {
            "sam_account_name": request.sam_account_name,
		    "group_name": request.group_name
            },
            "execution_result": result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
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

    try:

        result = ldap.remove_group_member(
            request.sam_account_name,
	        request.group_name
        )

        execution_contract = {
            "state": "ACTION_SUCCESS",
            "action": "remove_group_member",
            "proposed_action_payload": {
            "sam_account_name": request.sam_account_name,
		    "group_name": request.group_name
            },
            "execution_result": result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }
    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
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
    try:

        result = ldap.move_user_to_ou(
            request.sam_account_name,
            request.target_ou_dn
            )

        execution_contract = {
            "state": "ACTION_SUCCESS",
            "action": "move_user_to_ou",
            "proposed_action_payload": {
            "sam_account_name": request.sam_account_name,
		    "target_ou_dn": request.target_ou_dn
            },
            "execution_result": result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

    except Exception as ex:
    
            raise HTTPException(
                status_code=500,
                detail=str(ex)
            )


@router.post(
    "/disable-computer"
)
def disable_computer(
    request: DisableComputerRequest,

    current_user=Depends(
        require_group(
            [
                "ad_computer_mgmt"
            ]
        )
    )
):

    try:

        result = ldap.disable_computer(
            request.computer_name
        )

        execution_contract = {
            "state":
                "ACTION_SUCCESS",

            "action":
                "disable_computer",

            "proposed_action_payload": {
                "computer_name":
                    request.computer_name
            },

            "execution_result":
                result
        }

        message = (
            generate_execution_response(
                execution_contract
            )
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

@router.post("/verify-admin-secret")
def verify_admin_secret(
    request: VerifySecretRequest
):

    return {
        "success":
            request.secret ==
            ADMIN_APPROVAL_SECRET
    }


@router.post(
    "/update-user-displayname"
)
def update_user_displayname(
    request: UpdateUserDisplayNameRequest,

    current_user=Depends(
        require_group(
            [
                "ad_modify_user"
            ]
        )
    )
):

    try:

        result = ldap.update_user_displayname(
            request.sam_account_name,
            request.new_value
        )

        execution_contract = {
            "state":
                "ACTION_SUCCESS",

            "action":
                "update_user_displayName",

            "proposed_action_payload": {
                "sam_account_name":
                    request.sam_account_name,

                "new_display_name":
                    request.new_value
            },

            "execution_result":
                result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

@router.post(
    "/update-user-department"
)
def update_user_department(
    request: UpdateUserDisplayNameRequest,

    current_user=Depends(
        require_group(
            [
                "ad_modify_user"
            ]
        )
    )
):

    try:

        result = ldap.update_user_department(
            request.sam_account_name,
            request.new_value
        )

        execution_contract = {
            "state":
                "ACTION_SUCCESS",

            "action":
                "update_user_department",

            "proposed_action_payload": {
                "sam_account_name":
                    request.sam_account_name,

                "new_department":
                    request.new_value
            },

            "execution_result":
                result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

@router.post(
    "/update-user-description"
)
def update_user_description(
    request: UpdateUserDisplayNameRequest,  # Dùng chung modle với DisplayName 

    current_user=Depends(
        require_group(
            [
                "ad_modify_user"
            ]
        )
    )
):

    try:

        result = ldap.update_user_description(
            request.sam_account_name,
            request.new_value
        )

        execution_contract = {
            "state":
                "ACTION_SUCCESS",

            "action":
                "update_user_description",

            "proposed_action_payload": {
                "sam_account_name":
                    request.sam_account_name,

                "new_description":
                    request.new_value
            },

            "execution_result":
                result
        }

        message = generate_execution_response(
            execution_contract
        )

        return {
            "success": True,
            "message": message,
            "execution_result": result
        }

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )