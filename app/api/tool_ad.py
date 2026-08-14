from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

import asyncio
import json
import queue
from Monitor.runtime_monitor_writer import (
    get_runtime_monitor_snapshot
)
from Monitor.monitor_writer import (
    search_records
)
from fastapi import Request
from fastapi.responses import StreamingResponse

from app.event.runtime_bus import (
    subscribe as runtime_subscribe,
    unsubscribe as runtime_unsubscribe
)
from app.event.monitor_bus import (
    subscribe as monitor_subscribe,
    unsubscribe as monitor_unsubscribe  
)

from app.auth.rbac import require_group

from app.models.ad_tool import (
    DisableUserRequest,
    AddGroupRequest,
    RemoveGroupRequest,
    MoveUserRequest,
    VerifySecretRequest,
    DisableComputerRequest,
    UpdateUserDisplayNameRequest,
    DetectionFeedbackRequest
)
from app.agent.execution_response import (
    generate_execution_response
)
from app.adapters.ldap_adapter import (
    LDAPAdapter
)
from app.event.feedback_builder import (
    get_detection_event_by_id,
    build_detection_feedback_event,
    save_detection_feedback_dataset
)
from app.event.event_emitter import emit_event
from app.config import *
from app.adapters.ldap_container import (
    ldap,
)

router = APIRouter()

# ldap = LDAPAdapter()

# ldap.connect(
#     LDAP_HOST,
#     LDAP_USER,
#     LDAP_PASSWORD
# )

@router.post("/disable-user")
def disable_user(
    request: DisableUserRequest,

    current_user=Depends(
        require_group(
            [
                "ad_status_user"
            ]
        )
    )
):
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="disable_user",

        request=request.model_dump()
    )

    emit_event(
        event_name="ACTION_STARTED",

        action="disable_user",

        request=request.model_dump()
    )

    try:

        result = ldap.disable_user(
            request.sam_account_name
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="disable_user",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="disable_user",

            request=request.model_dump(),

            error=str(ex)
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

@router.post("/enable-user")
def enable_user(
    request: DisableUserRequest,

    current_user=Depends(
        require_group(
            [
                "ad_status_user"
            ]
        )
    )
):
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="enable_user",

        request=request.model_dump()
    )

    emit_event(
        event_name="ACTION_STARTED",

        action="enable_user",

        request=request.model_dump()
    )

    try:

        result = ldap.enable_user(
            request.sam_account_name
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="enable_user",

            request=request.model_dump(),

            execution_result=result
        )


        execution_contract = {
            "state": "ACTION_SUCCESS",
            "action": "enable_user",
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
        emit_event(
            event_name="ACTION_FAILED",

            action="enable_user",

            request=request.model_dump(),

            error=str(ex)
        )

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
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="add_group_member",

        request=request.model_dump()
    )

    emit_event(
        event_name="ACTION_STARTED",

        action="add_group_member",

        request=request.model_dump()
    )

    try:

        result = ldap.add_group_member(
            request.sam_account_name,
	    request.group_name
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="add_group_member",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="add_group_member",

            request=request.model_dump(),

            error=str(ex)
        )
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
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="remove_group_member",

        request=request.model_dump()
    )

    emit_event(
        event_name="ACTION_STARTED",

        action="remove_group_member",

        request=request.model_dump()
    )

    try:

        result = ldap.remove_group_member(
            request.sam_account_name,
	        request.group_name
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="remove_group_member",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="remove_group_member",

            request=request.model_dump(),

            error=str(ex)
        )
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
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="move_user_to_ou",

        request=request.model_dump()
    )

    emit_event(
        event_name="ACTION_STARTED",

        action="move_user_to_ou",

        request=request.model_dump()
    )

    try:

        result = ldap.move_user_to_ou(
            request.sam_account_name,
            request.target_ou_dn
            )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="move_user_to_ou",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="move_user_to_ou",

            request=request.model_dump(),

            error=str(ex)
        )
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
    emit_event(
            event_name="CONFIRM_ACCEPTED",
    
            action="disable_computer",
    
            request=request.model_dump()
        )
    
    emit_event(
            event_name="ACTION_STARTED",
    
            action="disable_computer",
    
            request=request.model_dump()
        )

    try:

        result = ldap.disable_computer(
            request.computer_name
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="disable_computer",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="disable_computer",

            request=request.model_dump(),

            error=str(ex)
        )
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
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="update_user_displayName",

        request=request.model_dump()
    )
    emit_event(
        event_name="ACTION_STARTED",

        action="update_user_displayName",

        request=request.model_dump()
    )

    try:

        result = ldap.update_user_displayname(
            request.sam_account_name,
            request.new_value
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="update_user_displayName",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="update_user_displayName",

            request=request.model_dump(),

            error=str(ex)
        )

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
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="update_user_department",

        request=request.model_dump()
    )
    emit_event(
        event_name="ACTION_STARTED",

        action="update_user_department",

        request=request.model_dump()
    )

    try:

        result = ldap.update_user_department(
            request.sam_account_name,
            request.new_value
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="update_user_department",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="update_user_department",

            request=request.model_dump(),

            error=str(ex)
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

@router.post(
    "/update-user-ip-phone"
)
def update_user_ip_phone(
    request: UpdateUserDisplayNameRequest,

    current_user=Depends(
        require_group(
            [
                "ad_modify_user"
            ]
        )
    )
):
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="update_user_ip_phone",

        request=request.model_dump()
    )
    emit_event(
        event_name="ACTION_STARTED",

        action="update_user_ip_phone",

        request=request.model_dump()
    )

    try:

        result = ldap.update_user_ip_phone(
            request.sam_account_name,
            request.new_value
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="update_user_ip_phone",

            request=request.model_dump(),

            execution_result=result
        )

        execution_contract = {
            "state":
                "ACTION_SUCCESS",

            "action":
                "update_user_ip_phone",

            "proposed_action_payload": {
                "sam_account_name":
                    request.sam_account_name,

                "new_ip_phone":
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
        emit_event(
            event_name="ACTION_FAILED",

            action="update_user_ip_phone",

            request=request.model_dump(),

            error=str(ex)
        )

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
    emit_event(
        event_name="CONFIRM_ACCEPTED",

        action="update_user_description",

        request=request.model_dump()
    )
    emit_event(
        event_name="ACTION_STARTED",

        action="update_user_description",

        request=request.model_dump()
    )

    try:

        result = ldap.update_user_description(
            request.sam_account_name,
            request.new_value
        )
        emit_event(
            event_name="ACTION_COMPLETED",

            action="update_user_description",

            request=request.model_dump(),

            execution_result=result
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
        emit_event(
            event_name="ACTION_FAILED",

            action="update_user_description",

            request=request.model_dump(),

            error=str(ex)
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )

@router.get(
    "/runtime-events/stream"
)
async def stream_runtime_events(
    request: Request,

    current_user=Depends(
        require_group(
            [
                "ad_login"
            ]
        )
    )
):

    print(
    "============= SSE ENTERED ============="
    )
    
    subscriber_queue = runtime_subscribe()

    async def event_generator():
        try:
            yield ": connected\n\n"

            while True:

                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.to_thread(
                        subscriber_queue.get,
                        True,
                        15
                    )
                    print(
                        "SSE GOT EVENT =",
                        event
                    )

                except queue.Empty:
                    yield ": heartbeat\n\n"
                    continue

                yield (
                    "event: runtime_event\n"
                    "data: "
                    + json.dumps(
                        event,
                        ensure_ascii=False
                    )
                    + "\n\n"
                )

        finally:
            runtime_unsubscribe(
                subscriber_queue
            )

            print(
                "RUNTIME SSE DISCONNECTED"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post(
    "/feedback/detection"
)
def submit_detection_feedback(
    request: DetectionFeedbackRequest,

    current_user=Depends(
        require_group(
            [
                "ad_modify_user"
            ]
        )
    )
):
    try:

        detection_event = (
            get_detection_event_by_id(
                request.event_id
            )
        )

        if not detection_event:
            return {
                "success": False,
                "message":
                    "Detection event not found"
            }

        feedback_event = (
            build_detection_feedback_event(
                detection_event,
                request.feedback
            )
        )

        save_detection_feedback_dataset(
            feedback_event
        )

        return {
            "success": True,
            "message":
                "Detection feedback saved"
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(
                e
            )
        }

#==============================================
# MONITOR DASHBOARD REFRESH API
#==============================================
@router.get(
    "/monitor/stream"
)
async def stream_monitor(
    request: Request
):
    subscriber_queue = monitor_subscribe()

    async def event_generator():
        try:
            yield ": connected\n\n"

            while True:

                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.to_thread(
                        subscriber_queue.get,
                        True,
                        15
                    )
                    print(
                        "SSE GOT EVENT =",
                        event
                    )

                except queue.Empty:
                    yield ": heartbeat\n\n"
                    continue

                yield (
                    "event: monitor_refresh\n"
                    "data: "
                    + json.dumps(event)
                    + "\n\n"
                )
        finally:
            monitor_unsubscribe(
                subscriber_queue
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
@router.get(
    "/monitor/dashboard"
)
def get_monitor_dashboard():
    return get_runtime_monitor_snapshot()


@router.get(
    "/monitor/search"
)
def search_monitor(
    object_type: str = None,
    action_user: str = None,
    object_name: str = None,
    from_date: str = None,
    to_date: str = None
):

    return search_records(
        object_type=object_type,
        action_user=action_user,
        object_name=object_name,
        from_date=from_date,
        to_date=to_date
    )