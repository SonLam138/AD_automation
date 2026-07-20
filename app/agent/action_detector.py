from app.agent.action_registry import (
    ACTION_REGISTRY
)


def normalize_text(
    text: str
):
    if text is None:
        return ""

    return (
        text
        .strip()
        .lower()
    )


def detect_action_by_hint(
    user_text: str
):
    """
    Phase v0 action detector.

    Rule:
    - Detect action only.
    - Do not search user/group/ou here.
    - Do not infer objects here.
    - If action is unknown, return NEED_ACTION_CLARIFICATION.
    """

    normalized_text = normalize_text(
        user_text
    )

    if not normalized_text:

        return {
            "success": False,
            "status": "NEED_ACTION_CLARIFICATION",
            "action": None,
            "confidence": 0,
            "message": "User input is empty",
            "requirements": []
        }

    matched_actions = []

    for action_key, action_config in (
        ACTION_REGISTRY.items()
    ):

        hints = action_config.get(
            "intent_hints",
            []
        )

        for hint in hints:

            normalized_hint = normalize_text(
                hint
            )

            if normalized_hint in normalized_text:

                matched_actions.append(
                    {
                        "action": action_key,
                        "hint": hint,
                        "score": len(
                            normalized_hint
                        )
                    }
                )

    if not matched_actions:

        return {
            "success": False,
            "status": "NEED_ACTION_CLARIFICATION",
            "action": None,
            "confidence": 0,
            "message": (
                "Cannot detect action. "
                "No search or action will be performed."
            ),
            "requirements": []
        }

    matched_actions = sorted(
        matched_actions,
        key=lambda item: item["score"],
        reverse=True
    )

    best_match = matched_actions[0]

    action_key = best_match["action"]

    action_config = ACTION_REGISTRY[
        action_key
    ]

    return {
        "success": True,
        "status": "ACTION_DETECTED",
        "action": action_key,
        "display_name": action_config[
            "display_name"
        ],
        "confidence": 1,
        "matched_hint": best_match["hint"],
        "requirements": action_config[
            "required_objects"
        ],
        "action_tool": action_config[
            "action_tool"
        ],
        "action_api": action_config[
            "action_api"
        ],
        "required_action_group":
            action_config[
                "required_action_group"
            ],
        "confirm_required":
            action_config[
                "confirm_required"
            ]
    }