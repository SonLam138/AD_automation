from app.agent.llm_action_detector import (
    detect_action_by_llm
)

from app.search_tools import (
    search_user,
    search_group,
    search_ou
)

from app.agent.pending_action_store import create_pending_action

SEARCH_TOOL_MAP = {
    "search_user": search_user,
    "search_group": search_group,
    "search_ou": search_ou,
}
from app.agent.pending_action_store import (
    get_pending_action,
    update_pending_action
)

from app.agent.action_handle import (
    handle_confirm_action,
    handle_admin_secret
)
from app.agent.response_planner import (
    generate_user_response
)

def _get_action_param_value(
    object_type: str,
    action_param: str,
    item: dict
):
    """
    Convert resolved AD object to action payload value.
    """

    if object_type == "USER":

        if action_param == "sam_account_name":
            return item.get(
                "sam_account_name"
            )

        if action_param == "user_dn":
            return item.get(
                "distinguished_name"
            )

    if object_type == "GROUP":

        if action_param == "group_name":
            return (
                item.get("cn")
                or item.get("name")
            )

        if action_param == "group_dn":
            return item.get(
                "distinguished_name"
            )

    if object_type == "OU":

        if action_param == "target_ou_dn":
            return item.get(
                "distinguished_name"
            )

        if action_param == "ou":
            return item.get(
                "ou"
            )

    return None


def _resolve_search_status(
    result: dict
):
    """
    Convert search result count to resolution status.
    """

    if not result.get(
        "success"
    ):
        return "SEARCH_FAILED"

    count = result.get(
        "count",
        0
    )

    if count == 0:
        return "NOT_FOUND"

    if count == 1:
        return "RESOLVED"

    return "AMBIGUOUS"

#===============================================
# OBJECT NEED SECRET KEY
#===============================================

SENSITIVE_USERS = {
    "administrator",
    "krbtgt",
    "sonnm"
}

SENSITIVE_GROUPS = {
    "domain admins",
    "enterprise admins",
    "administrators",
    "schema admins"
}


def get_approval_policy(
    action: str,
    resolved_objects: dict
):
    # Check User
    user = (resolved_objects.get("user") or resolved_objects.get("USER"))

    if user:
        username = (
            user.get("sam_account_name")
            or user.get("display_name")
            or ""
        ).lower()

        if username in SENSITIVE_USERS:
            return "admin_secret"

    # Check Group
    group = (resolved_objects.get("group") or resolved_objects.get("GROUP"))

    if group:
        group_name = (
            group.get("name")
            or group.get("cn")
            or ""
        ).lower()

        if group_name in SENSITIVE_GROUPS:
            return "admin_secret"

    return "normal"

#===============================================
# RESOVLER CHÍNH CHO CẢ HỆ
#===============================================

def resolve_action(
    user_text: str,
    ldap_connection
):
    """
    Resolve Action Phase

    Flow:
    Detect Action
        ↓
    Resolve Required Objects
        ↓
    Build Resolver Contract

    No confirmation.
    No execution.
    """

    detect_result = detect_action_by_llm(
        user_text
    )

    if not detect_result.get(
        "success"
    ):
        return {
            "status":
                "NEED_ACTION_CLARIFICATION",

            "state": "WAITING_ACTION",

            "next_step":
                "ASK_ACTION",

            "action":
                None,

            "target_object_type":
                None,

            "resolved_objects":
                {},

            "candidate_objects":
                {},

            "proposed_action_payload":
                {}
        }

    requirements = detect_result.get(
        "requirements",
        []
    )

    extracted_keywords = detect_result.get(
        "extracted_keywords",
        {}
    )

    action = detect_result.get(
        "action"
    )

    resolved_objects = {}

    candidate_objects = {}

    proposed_action_payload = {}

    final_status = "READY_TO_CONFIRM"

    next_step = "CONFIRM_ACTION"

    target_object_type = None
    state = None

    for requirement in requirements:

        object_type = requirement.get(
            "object_type"
        )

        search_tool_name = requirement.get(
            "search_tool"
        )

        action_param = requirement.get(
            "action_param"
        )

        keyword = extracted_keywords.get(
            object_type
        )

        #
        # NOT_FOUND
        #
        if not keyword:

            final_status = "NOT_FOUND"

            next_step = (
                "ASK_REQUIRED_OBJECT"
            )

            target_object_type = (
                object_type
            )
            state = "WAITING_REQUIRED_OBJECT"

            continue

        search_func = SEARCH_TOOL_MAP.get(
            search_tool_name
        )

        #
        # TOOL NOT FOUND
        #
        if not search_func:

            return {
                "status":
                    "SYSTEM_ERROR",

                "next_step":
                    None,

                "action":
                    action,

                "target_object_type":
                    object_type,

                "resolved_objects":
                    resolved_objects,

                "candidate_objects":
                    candidate_objects,

                "proposed_action_payload":
                    proposed_action_payload
            }

        search_result = search_func(
            ldap_connection,
            keyword,
            limit=100
        )

        count = search_result.get(
            "count",
            0
        )

        results = search_result.get(
            "results",
            []
        )

        #
        # NOT FOUND
        #
        if count == 0:

            if final_status != (
                "NEED_OBJECT_SELECTION"
            ):

                final_status = (
                    "NOT_FOUND"
                )

                next_step = (
                    "ASK_REQUIRED_OBJECT"
                )

                target_object_type = (
                    object_type
                )
                state = "WAITING_REQUIRED_OBJECT"

            continue

        #
        # NEED_OBJECT_SELECTION
        #
        if count > 1:

            final_status = (
                "NEED_OBJECT_SELECTION"
            )

            next_step = (
                "ASK_OBJECT_SELECTION"
            )

            target_object_type = (
                object_type
            )
            state = "WAITING_OBJECT_SELECTION"

            candidate_objects[
                object_type
            ] = results

            continue

        #
        # RESOLVED (count == 1)
        #
        item = results[0]

        resolved_objects[
            object_type
        ] = item

        value = _get_action_param_value(
            object_type=object_type,
            action_param=action_param,
            item=item
        )

        proposed_action_payload[
            action_param
        ] = value

    approval_policy = None
    #
    # READY TO CONFIRM
    #
    if (
        final_status
        == "READY_TO_CONFIRM"
    ):

        next_step = (
            "CONFIRM_ACTION"
        )

        target_object_type = None
        
        approval_policy = (
                get_approval_policy(
                    action=action,
                    resolved_objects=resolved_objects
                )
            )
        state = "CONFIRM_READY"


    result = {
        "status":
            final_status,

        "state":
            state,
        
        "next_step":
            next_step,

        "action":
            action,

        "target_object_type":
            target_object_type,

        "resolved_objects":
            resolved_objects,

        "candidate_objects":
            candidate_objects,

        "proposed_action_payload":
            proposed_action_payload,
        
        "approval_policy":
            approval_policy
    }

    #================================================
    # SAVE TURN 1 TO PENDING FILE
    # ===============================================    
    PENDING_STATUSES = {
    "READY_TO_CONFIRM",
    "NEED_OBJECT_SELECTION",
    "NOT_FOUND",
    "NEED_ACTION_CLARIFICATION"
    }

    if final_status in PENDING_STATUSES:

        action_id = create_pending_action(
            resolver_result=result
        )

        result["action_id"] = action_id


    # ==========================================
    # COPILOT RESPONSE
    # ==========================================

    try:

        result["message"] = (
            generate_user_response(
                resolver_result=result
            )
        )

    except Exception as ex:

        print(
            "GENERATE RESPONSE ERROR =",
            ex
        )

        result["message"] = (
            "Tôi đã xử lý yêu cầu nhưng chưa thể tạo phản hồi."
        )

    return result

#========================================================
# TURN 2 : CHUYỂN TỚI CÁC HÀM HANDLE ĐÚNG VỚI STATE 
#=======================================================

def handle_user_input(
    action_id: str,
    user_text: str
):
    """
    Entry point cho các turn tiếp theo.

    Chỉ đọc state hiện tại
    và route tới handler tương ứng.

    Không gọi LLM.
    Không detect lại action.
    Không execute action.
    """

    pending_action = get_pending_action(
        action_id
    )

    if not pending_action:
        return {
            "success": False,
            "state": "FAILED",
            "error": "Pending action not found"
        }

    state = pending_action.get(
        "state"
    )

    #
    # User xác nhận
    #
    if state == (
        "CONFIRM_READY"
    ):
        return handle_confirm_action(
            action_id,
            user_text
        )

    #
    # Chờ nhập admin secret
    #
    if state == (
        "WAITING_ADMIN_SECRET"
    ):
        return handle_admin_secret(
            action_id,
            user_text
        )

    #
    # Đã xác thực xong
    #
    if state == (
        "EXECUTION_READY"
    ):
        return {
            "success": True,
            "state": "EXECUTION_READY",
            "message": (
                "Yêu cầu đã sẵn sàng để thực thi."
            ),
            "pending_action": pending_action
        }

    #
    # User nhập sai xác nhận quá số lần
    #
    if state == (
        "CANCELLED"
    ):
        return {
            "success": False,
            "state": "CANCELLED",
            "message": (
                "Yêu cầu đã bị hủy."
            )
        }

    #
    # Future states
    #
    # WAITING_OBJECT_SELECTION
    # WAITING_REQUIRED_OBJECT
    # WAITING_APPROVER
    #

    return {
        "success": False,
        "state": state,
        "error": (
            f"Unsupported state: "
            f"{state}"
        )
    }



