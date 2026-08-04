
from app.utils.perf import PerfTimer
import time
from app.search_tools.messages import (
    build_missing_keyword_message,
    build_resolver_message
)
from app.agent.llm_action_detector import (
    detect_action_by_llm,
    detect_action
)

from app.search_tools import (
    search_user,
    search_group,
    search_ou,
    search_computer
)

from app.agent.pending_action_store import create_pending_action

from app.agent.pending_action_store import (
    get_pending_action,
    update_pending_action
)

from app.agent.action_handle import (
    handle_confirm_action,
    handle_admin_secret
)

from app.search_tools.filter_by_action import filter_candidates_by_action
from app.event.event_emitter import emit_event

SEARCH_TOOL_MAP = {
    "search_user": search_user,
    "search_group": search_group,
    "search_ou": search_ou,
    "search_computer": search_computer
}

def _get_action_param_value(
    object_type: str,
    action_param: str,
    item: dict
):
    """
    Convert resolved AD object to action payload value.
    Use in Happy Case ( count = 1)
    """

    if object_type == "USER":

        if action_param in (
            "sam_account_name",
            "displayname",
            "department",
            "description"
        ):
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

    if object_type == "COMPUTER":

        if action_param == "computer_name":
            return item.get(
                "computer_name"
            )    

    return None


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

SENSITIVE_COMPUTER_OUS = {
    "OU=Servers",
    "OU=Domain Controllers",
    "OU=PAMBT"
}

def get_approval_policy(
    action: str,
    resolved_objects: dict
):
    # Check User name
    user = (resolved_objects.get("user") or resolved_objects.get("USER"))

    if user:
        username = (
            user.get("sam_account_name")
            or user.get("display_name")
            or ""
        ).lower()

        if username in SENSITIVE_USERS:
            return "admin_secret"

    # Check Group name
    group = (resolved_objects.get("group") or resolved_objects.get("GROUP"))

    if group:
        group_name = (
            group.get("name")
            or group.get("cn")
            or ""
        ).lower()

        if group_name in SENSITIVE_GROUPS:
            return "admin_secret"
        
    # Check Computer in OU
    computer = (resolved_objects.get("computer") or resolved_objects.get("COMPUTER"))
    if computer:
        computer_dn = (
        computer.get("distinguished_name")
        or ""
        )
        for sensitive_ou in SENSITIVE_COMPUTER_OUS:
            if sensitive_ou.lower() in computer_dn.lower():
                return "admin_secret"

    return "normal"

    



def get_candidate_approval_policy(
    action: str,
    object_type: str,
    candidates: list
):
    """
    Nếu bất kỳ candidate nào yêu cầu
    admin_secret thì trả admin_secret.

    Ngược lại trả normal.
    """

    for item in candidates:

        policy = get_approval_policy(
            action=action,
            resolved_objects={
                object_type: item
            }
        )

        if policy == "admin_secret":
            return "admin_secret"

    return "normal"    

#===============================================
# RESOVLER CHÍNH CHO CẢ HỆ
#===============================================

def resolve_action(
    user_text: str,
    ldap_connection,
    username=None,
    request_id=None
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

    timer = PerfTimer(
    scope="RESOLVER"
)
    runtime_events = []
    timer.checkpoint(
        "START"
    )
    runtime_events.append(
        emit_event(
            event_name="QUERY_RECEIVED",
            request_id=request_id,
            user_query=user_text,
            username=username
        )
    )
    runtime_events.append(
        emit_event(
            event_name="DETECTION_STARTED",
            request_id=request_id,
            user_query=user_text
        )
    )
    detect_result = detect_action(
        user_text
    )
    print("detect_result")
    timer.checkpoint(
        "LLM_DETECT_ACTION"
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

            "new_value":
                {},
            "proposed_action_payload":
                {}
        }

    detection_event = emit_event(
        event_name="DETECTION_RESULT",

        user_query=user_text,

        detected_action=detect_result.get(
            "action"
        ),

        detected_keywords=detect_result.get(
            "extracted_keywords",
            {}
        ),

        requirements=detect_result.get(
            "requirements",
            []
        )
    )

    runtime_events.append(detection_event)

    requirements = detect_result.get(
        "requirements",
        []
    )

    extracted_keywords = detect_result.get(
        "extracted_keywords",
        {}
    )
    new_value = detect_result.get(
    "new_value"
    )

    action = detect_result.get(
        "action"
    )
    
    new_value = detect_result.get(
        "new_value"
    )

    message = ""
    
    resolved_objects = {}

    candidate_objects = {}

    proposed_action_payload = {}

    final_status = "READY_TO_CONFIRM"

    next_step = "CONFIRM_ACTION"

    approval_policy = None
    approval_policies = []

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
        payload_key = requirement.get("payload_key")

        keyword = extracted_keywords.get(
            object_type
        )
        timer.checkpoint(
            f"START_OBJECT_{object_type}"
        )

        #
        # MISSING KEYWORD
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

            message = build_missing_keyword_message(object_type)

            continue
        
        print(
            "OBJECT_TYPE =",
            object_type
            )
        print(
            "SEARCH_TOOL =",
            search_tool_name
            )
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

        runtime_events.append(
            emit_event(
                event_name="OBJECT_SEARCH_STARTED",
                request_id=request_id,
                action=action,
                object_type=object_type,
                keyword=keyword,
                search_tool=search_tool_name
            )
        )
        search_result = search_func(
            ldap_connection,
            keyword,
            limit=100
        )
        timer.checkpoint(
            "SEARCH_RESULT"
            )
        all_results = search_result.get(
            "results",
            []
        )
        results = filter_candidates_by_action(
            action,
            all_results
        )
        count = len(results)

        #
        # OBJECT DISABLED
        #
        if (
            len(all_results) == 1
            and all_results[0].get(
                "is_disabled",
                False
            )
        ):
            disabled_user = all_results[0]

            runtime_events.append(
                emit_event(
                    event_name="OBJECT_DISABLED",
                    request_id=request_id,

                    action=action,

                    object_type=object_type,

                    keyword=keyword,

                    object_name=disabled_user.get(
                        "sam_account_name"
                    )
                )
            )

            return {
                "status": "OBJECT_DISABLED",
                "state": "OBJECT_DISABLED",
                "message": (
                    f"Ngáo tìm thấy tài khoản "
                    f"{disabled_user.get('sam_account_name')} "
                    f"nhưng tài khoản hiện đang bị vô hiệu hóa (Disabled)."
                ),
                "disabled_object": disabled_user
            }

        #
        # OBJECT NOT FOUND
        #
        if count == 0:
            runtime_events.append(
                emit_event(
                    event_name="OBJECT_NOT_FOUND",
                    request_id=request_id,
                    action=action,
                    object_type=object_type,
                    keyword=keyword
                )
            )

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

            runtime_events.append(
                emit_event(
                    event_name="OBJECT_MULTI_MATCH",
                    request_id=request_id,
                    action=action,
                    object_type=object_type,
                    keyword=keyword,
                    match_count=count
                )
            )

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

            enriched_results = []

            for item in results:

                item_copy = dict(item)

                item_copy["approval_policy"] = (
                    get_candidate_approval_policy(
                        action=action,
                        object_type=object_type,
                        candidates=[item]
                    )
                )
                
                enriched_results.append(
                    item_copy
                )
            timer.checkpoint(
                "GET_CANDIDATE_POLICY"
            )
            candidate_objects[
                object_type
            ] = enriched_results

            approval_policy = (
            get_candidate_approval_policy(
            action=action,
            object_type=object_type,
            candidates=results
            ))
            runtime_events.append(
                emit_event(
                    event_name="APPROVAL_POLICY_RESOLVED",
                    request_id=request_id,

                    action=action,

                    object_type=object_type,

                    policy=approval_policy,

                    policy_source="MULTI_MATCH"
                )
            )

            continue

        #
        # RESOLVED (count == 1)
        #

        runtime_events.append(
            emit_event(
                event_name="OBJECT_FOUND",
                request_id=request_id,
                action=action,
                object_type=object_type,
                keyword=keyword
            )
        )
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
            payload_key
        ] = value
        
        new_value = detect_result.get(
            "new_value"
            )
        if new_value:
            proposed_action_payload[
            "new_value"
            ] = new_value

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
        runtime_events.append(
            emit_event(
            event_name="CONFIRM_READY",
            request_id=request_id,
            action=action,
            approval_policy=approval_policy,
            payload=proposed_action_payload
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

        "new_value":
            new_value,
        
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

    if message:
        result["message"] = message
    else:
        result["message"] = build_resolver_message(
            result
        )

    result["events"] = [runtime_events]

    timer.finish(
    "END"
    )

    print(result)
    return result


