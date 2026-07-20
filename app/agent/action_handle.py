<<<<<<< HEAD
from app.agent.pending_action_store import (
    get_pending_action,
    update_pending_action
)

from app.config import (
    ADMIN_APPROVAL_SECRET
)

def handle_confirm_action(
    action_id: str
):
    """
    User đã xác nhận action.

    CONFIRM_READY
        ->
    EXECUTION_READY

    hoặc

    WAITING_ADMIN_SECRET
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

    approval_policy = pending_action.get(
        "approval_policy",
        "normal"
    )

    #
    # Normal action
    #
    if approval_policy == (
        "normal"
    ):

        pending_action["state"] = (
            "EXECUTION_READY"
        )

        pending_action["next_step"] = (
            "EXECUTE_ACTION"
        )

        update_pending_action(
            action_id,
            pending_action
        )

        return {
            "success": True,

            "action_id": action_id,

            "state":
                "EXECUTION_READY",

            "next_step":
                "EXECUTE_ACTION",

            "pending_action":
                pending_action
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

        pending_action["next_step"] = (
            "ASK_ADMIN_SECRET"
        )

        update_pending_action(
            action_id,
            pending_action
        )

        return {
            "success": True,

            "action_id": action_id,

            "state":
                "WAITING_ADMIN_SECRET",

            "next_step":
                "ASK_ADMIN_SECRET",

            "pending_action":
                pending_action
        }

    return {
        "success": False,
        "state": "FAILED",
        "error": (
            f"Unknown approval policy: "
            f"{approval_policy}"
        )
    }

#=====================================================

def validate_admin_secret(
    secret: str
) -> bool:
    return (
        secret.strip()
        == ADMIN_APPROVAL_SECRET.strip()
    )

#=====================================================
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
            "error":
                f"Invalid state: {current_state}"
        }

    if not validate_admin_secret(
        user_text
    ):
        return {
            "success": False,
            "state":
                "WAITING_ADMIN_SECRET",
            "error":
                "Invalid admin secret"
        }

    pending_action["state"] = (
        "EXECUTION_READY"
    )

    pending_action["next_step"] = (
        "EXECUTE_ACTION"
    )

    update_pending_action(
        action_id,
        pending_action
    )

    return {
        "success": True,

        "action_id":
            action_id,

        "state":
            "EXECUTION_READY",

        "next_step":
            "EXECUTE_ACTION",

        "pending_action":
            pending_action
    }
=======
# from app.agent.pending_action_store import (
#     get_pending_action,
#     update_pending_action
# )

# # from app.config import (
# #     ADMIN_APPROVAL_SECRET
# # )

# def handle_confirm_action(
#     action_id: str
# ):
#     """
#     User đã xác nhận action.

#     CONFIRM_READY
#         ->
#     EXECUTION_READY

#     hoặc

#     WAITING_ADMIN_SECRET
#     """

#     pending_action = get_pending_action(
#         action_id
#     )

#     if not pending_action:
#         return {
#             "success": False,
#             "state": "FAILED",
#             "error": "Pending action not found"
#         }

#     current_state = pending_action.get(
#         "state"
#     )

#     if current_state != (
#         "CONFIRM_READY"
#     ):
#         return {
#             "success": False,
#             "state": current_state,
#             "error": (
#                 f"Invalid state: "
#                 f"{current_state}"
#             )
#         }

#     approval_policy = pending_action.get(
#         "approval_policy",
#         "normal"
#     )

#     #
#     # Normal action
#     #
#     if approval_policy == (
#         "normal"
#     ):

#         pending_action["state"] = (
#             "EXECUTION_READY"
#         )

#         pending_action["next_step"] = (
#             "EXECUTE_ACTION"
#         )

#         update_pending_action(
#             action_id,
#             pending_action
#         )

#         return {
#             "success": True,

#             "action_id": action_id,

#             "state":
#                 "EXECUTION_READY",

#             "next_step":
#                 "EXECUTE_ACTION",

#             "pending_action":
#                 pending_action
#         }

#     #
#     # Sensitive action
#     #
#     if approval_policy == (
#         "admin_secret"
#     ):

#         pending_action["state"] = (
#             "WAITING_ADMIN_SECRET"
#         )

#         pending_action["next_step"] = (
#             "ASK_ADMIN_SECRET"
#         )

#         update_pending_action(
#             action_id,
#             pending_action
#         )

#         return {
#             "success": True,

#             "action_id": action_id,

#             "state":
#                 "WAITING_ADMIN_SECRET",

#             "next_step":
#                 "ASK_ADMIN_SECRET",

#             "pending_action":
#                 pending_action
#         }

#     return {
#         "success": False,
#         "state": "FAILED",
#         "error": (
#             f"Unknown approval policy: "
#             f"{approval_policy}"
#         )
#     }

# #=====================================================

# def validate_admin_secret(
#     secret: str
# ) -> bool:
#     return (
#         secret.strip()
#         == ADMIN_APPROVAL_SECRET.strip()
#     )

# #=====================================================
# def handle_admin_secret(
#     action_id: str,
#     user_text: str
# ):
#     """
#     WAITING_ADMIN_SECRET
#         ->
#     EXECUTION_READY
#     """

#     pending_action = get_pending_action(
#         action_id
#     )

#     if not pending_action:
#         return {
#             "success": False,
#             "error": "Pending action not found"
#         }

#     current_state = pending_action.get(
#         "state"
#     )

#     if current_state != (
#         "WAITING_ADMIN_SECRET"
#     ):
#         return {
#             "success": False,
#             "error":
#                 f"Invalid state: {current_state}"
#         }

#     if not validate_admin_secret(
#         user_text
#     ):
#         return {
#             "success": False,
#             "state":
#                 "WAITING_ADMIN_SECRET",
#             "error":
#                 "Invalid admin secret"
#         }

#     pending_action["state"] = (
#         "EXECUTION_READY"
#     )

#     pending_action["next_step"] = (
#         "EXECUTE_ACTION"
#     )

#     update_pending_action(
#         action_id,
#         pending_action
#     )

#     return {
#         "success": True,

#         "action_id":
#             action_id,

#         "state":
#             "EXECUTION_READY",

#         "next_step":
#             "EXECUTE_ACTION",

#         "pending_action":
#             pending_action
#     }
>>>>>>> main


