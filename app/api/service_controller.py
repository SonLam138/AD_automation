from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from ldap3 import MODIFY_ADD, MODIFY_DELETE
from typing import Any, Callable
from app.auto_engine.models.employee_offboarding import (
    EmployeeOffboardingApiRequest
)
from app.api.workflow_request import create_offboarding_plan
from app.auth.dependencies import (
    require_service_token,
    require_integration_token
)
from app.auth.integration_registry import INTEGRATION_CLIENTS
from app.auth.jwt_handler import create_integration_token
from app.auth.integration_token_request import IntegrationTokenRequest
from app.adapters.ldap_container import ldap
from app.search_tools.integration_resolve_group import (
    integration_resolve_group,
)
from app.search_tools.integration_resolve_ou import (
    integration_resolve_ou,
)
from app.search_tools.integration_resolve_group_member import (
    integration_resolve_group_member,
)
from app.models.ad_tool import (
    CreateAdUserRequest,
    CreateGroupRequest,
    DisableComputerRequest,
    DisableUserRequest,
    IntegrationGroupMemberRequest,
    IntegrationMoveToOuRequest,
    UpdateUserDisplayNameRequest,
)
from app.auth.integration_authorization import (require_integration_endpoint)



router = APIRouter()


def _execute_integration_ad_action(
    operation: Callable[[], Any],
    *,
    require_success: bool = False,
):
    try:
        result = operation()

        if (
            require_success
            and isinstance(result, dict)
            and result.get("success") is False
        ):
            raise HTTPException(
                status_code=500,
                detail=result,
            )

        return result

    except HTTPException:
        raise

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )


def _require_unique_integration_target(
    result: dict,
    object_type: str,
) -> str:
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=(
                f"{object_type} lookup failed: "
                f"{result.get('message', 'Unknown LDAP error')}"
            ),
        )

    count = result.get("count", 0)

    if count == 0:
        raise HTTPException(
            status_code=404,
            detail=f"No matching {object_type} found",
        )

    if count != 1:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Ambiguous {object_type} lookup: "
                f"{count} exact matches found"
            ),
        )

    distinguished_name = (
        result["results"][0].get(
            "distinguished_name"
        )
    )

    if not distinguished_name:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Resolved {object_type} has no distinguished name"
            ),
        )

    return distinguished_name


def _integration_group_member_action(
    request: IntegrationGroupMemberRequest,
    modify_operation: int,
):
    group_result = _execute_integration_ad_action(
        lambda: integration_resolve_group(
            connection=ldap.connection,
            target_group=request.target_group,
            target_group_email=request.target_group_email,
            target_group_ou=request.target_group_ou,
        )
    )
    group_dn = _require_unique_integration_target(
        group_result,
        "group",
    )

    if request.object_type == "user":
        operation = (
            ldap.add_group_member_by_dn
            if modify_operation == MODIFY_ADD
            else ldap.remove_group_member_by_dn
        )

        return _execute_integration_ad_action(
            lambda: operation(
                request.sam_account_name,
                group_dn,
            )
        )

    member_result = _execute_integration_ad_action(
        lambda: integration_resolve_group_member(
            connection=ldap.connection,
            object_type=request.object_type,
            computer_name=request.computer_name,
            group_name=request.group_name,
            group_email=request.member_group_email,
            group_ou=request.member_group_ou,
        )
    )
    member_dn = _require_unique_integration_target(
        member_result,
        f"{request.object_type} member",
    )

    success = _execute_integration_ad_action(
        lambda: ldap.connection.modify(
            group_dn,
            {
                "member": [
                    (
                        modify_operation,
                        [member_dn],
                    )
                ]
            },
        )
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail=ldap.connection.result,
        )

    return {
        "success": True,
        "action": (
            "add_group_member"
            if modify_operation == MODIFY_ADD
            else "remove_group_member"
        ),
        "object_type": request.object_type,
        "member_dn": member_dn,
        "group_dn": group_dn,
    }


@router.post(
    "/employee-offboarding"
)
def service_employee_offboarding(
    source_request:
        EmployeeOffboardingApiRequest,

    claims=Depends(
        require_service_token
    )
):

    try:

        return create_offboarding_plan(
            source_request
        )

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )


@router.post("/integration/ad/users/create")
def integration_ad_create_user(
    request: CreateAdUserRequest,
    claims=Depends(require_integration_endpoint("create_object")),
):
    if not request.display_name:
        request.display_name = request.full_name

    result = _execute_integration_ad_action(
        lambda: ldap.create_user(
            request,
            approved_by=claims.get("sub"),
            approved_name=claims.get("sub"),
            approval_type="INTEGRATION",
        ),
        require_success=True,
    )

    return result


@router.post("/integration/ad/users/disable")
def integration_ad_disable_user(
    request: DisableUserRequest,
    claims=Depends(require_integration_endpoint("disable_object")),
):
    return _execute_integration_ad_action(
        lambda: ldap.disable_user(
            request.sam_account_name
        )
    )


@router.post("/integration/ad/users/enable")
def integration_ad_enable_user(
    request: DisableUserRequest,
    claims=Depends(require_integration_endpoint("enable_object")),
):
    return _execute_integration_ad_action(
        lambda: ldap.enable_user(
            request.sam_account_name
        )
    )


@router.post("/integration/ad/users/update-display-name")
def integration_ad_update_user_display_name(
    request: UpdateUserDisplayNameRequest,
    claims=Depends(require_integration_endpoint("basic_attribute")),
):
    return _execute_integration_ad_action(
        lambda: ldap.update_user_displayname(
            request.sam_account_name,
            request.new_value,
        )
    )


@router.post("/integration/ad/users/update-department")
def integration_ad_update_user_department(
    request: UpdateUserDisplayNameRequest,
    claims=Depends(require_integration_endpoint("basic_attribute")),
):
    return _execute_integration_ad_action(
        lambda: ldap.update_user_department(
            request.sam_account_name,
            request.new_value,
        )
    )


@router.post("/integration/ad/users/update-ip-phone")
def integration_ad_update_user_ip_phone(
    request: UpdateUserDisplayNameRequest,
    claims=Depends(require_integration_endpoint("basic_attribute")),
):
    return _execute_integration_ad_action(
        lambda: ldap.update_user_ip_phone(
            request.sam_account_name,
            request.new_value,
        )
    )


@router.post("/integration/ad/users/update-description")
def integration_ad_update_user_description(
    request: UpdateUserDisplayNameRequest,
    claims=Depends(require_integration_endpoint("basic_attribute")),
):
    return _execute_integration_ad_action(
        lambda: ldap.update_user_description(
            request.sam_account_name,
            request.new_value,
        )
    )


@router.post("/integration/ad/group-members/add")
def integration_ad_add_user_to_group(
    request: IntegrationGroupMemberRequest,
    claims=Depends(require_integration_endpoint("group_member_add")),
):
    return _integration_group_member_action(
        request,
        MODIFY_ADD,
    )


@router.post("/integration/ad/group-members/remove")
def integration_ad_remove_user_from_group(
    request: IntegrationGroupMemberRequest,
    claims=Depends(require_integration_endpoint("group_member_remove")),
):
    return _integration_group_member_action(
        request,
        MODIFY_DELETE,
    )


@router.post("/integration/ad/move-to-ou")
def integration_ad_move_to_ou(
    request: IntegrationMoveToOuRequest,
    claims=Depends(require_integration_endpoint("move_to_ou")),
):
    ou_result = _execute_integration_ad_action(
        lambda: integration_resolve_ou(
            connection=ldap.connection,
            target_ou=request.target_ou,
            target_ou_parent=request.target_ou_parent,
        )
    )
    ou_dn = _require_unique_integration_target(
        ou_result,
        "OU",
    )

    if request.object_type == "user":
        operation = lambda: ldap.move_user_to_ou(
            request.sam_account_name,
            ou_dn,
        )
    elif request.object_type == "computer":
        operation = lambda: ldap.move_computer_to_ou(
            request.computer_name,
            ou_dn,
        )
    else:
        operation = lambda: ldap.move_group_to_ou(
            request.group_name,
            ou_dn,
        )

    return _execute_integration_ad_action(operation)


@router.post("/integration/ad/computers/disable")
def integration_ad_disable_computer(
    request: DisableComputerRequest,
    claims=Depends(require_integration_endpoint("disable_object")),
):
    return _execute_integration_ad_action(
        lambda: ldap.disable_computer(
            request.computer_name
        )
    )


@router.post("/integration/ad/groups/create")
def integration_ad_create_group(
    request: CreateGroupRequest,
    claims=Depends(require_integration_endpoint("create_object")),
):
    return _execute_integration_ad_action(
        lambda: ldap.create_group(
            request.group_name,
            request.target_ou_dn,
            request.description,
        )
    )


@router.post(
    "/integration/token"
)
def integration_token(
    request:
        IntegrationTokenRequest
):

    client = (
        INTEGRATION_CLIENTS.get(
            request.client_id
        )
    )

    if not client:

        raise HTTPException(
            status_code=401,
            detail="Invalid client_id"
        )

    if (
        not client["enabled"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Client disabled"
        )

    if (
        client["client_secret"]
        != request.client_secret
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid client_secret"
        )

    token = (
        create_integration_token(
            request.client_id
        )
    )

    return {

        "access_token":
            token,

        "token_type":
            "bearer",

        "client_id":
            request.client_id,
    }

@router.post(
    "/integration/employee-offboarding"
)
def integration_employee_offboarding(

    source_request:
        EmployeeOffboardingApiRequest,

    claims=Depends(
        require_integration_token
    )
):

    try:

        return create_offboarding_plan(
            source_request
        )

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )
    