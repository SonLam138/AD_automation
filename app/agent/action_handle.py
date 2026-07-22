from datetime import datetime

from app.agent.pending_action_store import (
    get_pending_action,
    update_pending_action
)

from app.config import (
    ADMIN_APPROVAL_SECRET
)

CONFIRM_WORDS = {
    "ok",
    "oke",
    "yes",
    "y",
    "confirm",
    "đồng ý",
    "dong y",
    "xác nhận",
    "xac nhan"
}


# =====================================================
# HELPER
# =====================================================
def is_confirm_text(
    user_text: str
) -> bool:

    if not user_text:
        return False

    return (
        user_text.strip().lower()
        in CONFIRM_WORDS
    )

# =====================================================
# CONFIRM
# =====================================================

from datetime import datetime

MAX_CONFIRM_RETRY = 2


def handle_confirm_action(
    action_id: str,
    user_text: str
):
    """
    CONFIRM_READY
        ->
    EXECUTION_READY

    hoặc

    CONFIRM_READY
        ->
    WAITING_ADMIN_SECRET

    Sai xác nhận 2 lần
        ->
    CANCELLED
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

    current_state = pending_action.get(
        "state"
    )

    if current_state != (
        "CONFIRM_READY"
    ):
        return {
            "success": False,
            "state": current_state,
            "error": (
                f"Invalid state: "
                f"{current_state}"
            )
        }

    #
    # Validate confirm text
    #
    if not is_confirm_text(
        user_text
    ):

        retry_count = pending_action.get(
            "confirm_retry_count",
            0
        )

        retry_count += 1

        pending_action[
            "confirm_retry_count"
        ] = retry_count

        #
        # Retry exceeded
        #
        if retry_count >= (
            MAX_CONFIRM_RETRY
        ):

            pending_action["state"] = (
                "CANCELLED"
            )

            pending_action[
                "cancel_reason"
            ] = (
                "Invalid confirmation input"
            )

            pending_action[
                "cancelled_at"
            ] = (
                datetime.now().isoformat()
            )

            update_pending_action(
                action_id,
                pending_action
            )

            return {
                "success": False,
                "action_id": action_id,
                "state": "CANCELLED",
                "message": (
                    "Yêu cầu đã bị hủy do xác nhận không hợp lệ."
                )
            }

        update_pending_action(
            action_id,
            pending_action
        )

        return {
            "success": True,
            "action_id": action_id,
            "state": "CONFIRM_READY",
            "message": (
                "Bạn vui lòng nhập đúng thông tin xác nhận. "
                "Bạn còn 1 lần xác nhận."
            )
        }

    approval_policy = pending_action.get(
        "approval_policy"
    )

    if not approval_policy:
        return {
            "success": False,
            "state": "FAILED",
            "error": "Missing approval_policy"
        }

    #
    # Normal action
    #
    if approval_policy == (
        "normal"
    ):

        pending_action["state"] = (
            "EXECUTION_READY"
        )

        pending_action[
            "confirmed_at"
        ] = (
            datetime.now().isoformat()
        )

        update_pending_action(
            action_id,
            pending_action
        )

        return {
            "success": True,
            "action_id": action_id,
            "state": "EXECUTION_READY",
            "message": (
                "Yêu cầu đã sẵn sàng để thực thi."
            ),
            "pending_action": pending_action
        }

    #
    # Sensitive action
    #
    if approval_policy == (
        "admin_secret"
    ):

        pending_action["state"] = (
            "WAITING_ADMIN_SECRET"
        )

        pending_action[
            "confirmed_at"
        ] = (
            datetime.now().isoformat()
        )

        update_pending_action(
            action_id,
            pending_action
        )

        return {
            "success": True,
            "action_id": action_id,
            "state": (
                "WAITING_ADMIN_SECRET"
            ),
            "message": (
                "Vui lòng nhập mã xác nhận quản trị."
            ),
            "pending_action": pending_action
        }

    return {
        "success": False,
        "state": "FAILED",
        "error": (
            f"Unknown approval policy: "
            f"{approval_policy}"
        )
    }

# =====================================================
# SECRET VALIDATION
# =====================================================

def validate_admin_secret(
    secret: str
) -> bool:

    if not secret:
        return False

    return (
        secret.strip()
        ==
        ADMIN_APPROVAL_SECRET.strip()
    )


# =====================================================
# ADMIN SECRET
# =====================================================

def handle_admin_secret(
    action_id: str,
    user_text: str
):
    """
    WAITING_ADMIN_SECRET
        ->
    EXECUTION_READY
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

    current_state = pending_action.get(
        "state"
    )

    if current_state != (
        "WAITING_ADMIN_SECRET"
    ):
        return {
            "success": False,
            "state": current_state,
            "error": (
                f"Invalid state: "
                f"{current_state}"
            )
        }

    if not validate_admin_secret(
        user_text
    ):
        return {
            "success": False,
            "state": (
                "WAITING_ADMIN_SECRET"
            ),
            "error": (
                "Invalid admin secret"
            )
        }

    pending_action["state"] = (
        "EXECUTION_READY"
    )

    pending_action[
        "secret_validated"
    ] = True

    pending_action[
        "secret_validated_at"
    ] = datetime.now().isoformat()

    update_pending_action(
        action_id,
        pending_action
    )

    return {
        "success": True,
        "action_id": action_id,
        "state": "EXECUTION_READY",
        "message": (
            "Action is ready to execute"
        ),
        "pending_action": pending_action
    }