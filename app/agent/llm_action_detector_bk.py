import json
import re

from app.agent.action_prompt import (
    build_action_detection_prompt
)

from app.agent.action_registry import (
    ACTION_REGISTRY
)

from app.agent.llm_client import (
    ask_llm
)


MIN_ACTION_CONFIDENCE = 0.70


def _extract_json(
    raw_text: str
):

    if not raw_text:
        return None

    text = raw_text.strip()

    try:
        return json.loads(
            text
        )

    except Exception:
        pass

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        return None

    try:
        return json.loads(
            match.group(0)
        )

    except Exception:
        return None


def _build_stop_response(
    user_text: str,
    reason: str,
    raw_llm_response=None
):

    return {
        "success": False,
        "status": "NEED_ACTION_CLARIFICATION",
        "action": None,
        "confidence": 0,
        "message": reason,
        "requirements": [],
        "raw_llm_response": raw_llm_response,
        "user_text": user_text
    }


def detect_action_by_llm(
    user_text: str
):
    """
    LLM Action Detector v0.

    IMPORTANT:
    - LLM only detects action.
    - Requirements are loaded from registry.
    - No search here.
    - No action here.
    """

    if not user_text or not user_text.strip():

        return _build_stop_response(
            user_text=user_text,
            reason="User input is empty"
        )

    prompt = build_action_detection_prompt(
        user_text
    )

    raw_response = ask_llm(
        prompt
    )

    parsed = _extract_json(
        raw_response
    )

    if not parsed:

        return _build_stop_response(
            user_text=user_text,
            reason="LLM did not return valid JSON",
            raw_llm_response=raw_response
        )

    action = parsed.get(
        "action"
    )

    confidence = float(
        parsed.get(
            "confidence",
            0
        )
    )

    reason = parsed.get(
        "reason",
        ""
    )

    if action in [
        None,
        "",
        "null"
    ]:

        return _build_stop_response(
            user_text=user_text,
            reason=(
                "LLM cannot determine action"
            ),
            raw_llm_response=parsed
        )

    if action not in ACTION_REGISTRY:

        return _build_stop_response(
            user_text=user_text,
            reason=(
                f"Unsupported action returned by LLM: {action}"
            ),
            raw_llm_response=parsed
        )

    if confidence < MIN_ACTION_CONFIDENCE:

        return _build_stop_response(
            user_text=user_text,
            reason=(
                f"Action confidence too low: {confidence}"
            ),
            raw_llm_response=parsed
        )

    action_config = ACTION_REGISTRY[
        action
    ]
    
    extracted_keywords = parsed.get(
        "extracted_keywords",
        {}
    )

    if not isinstance(
        extracted_keywords,
        dict
    ):
        extracted_keywords = {}

    return {
        "success": True,
        "status": "ACTION_DETECTED",
        "action": action,
        "display_name": action_config.get(
            "display_name"
        ),
        "confidence": confidence,
        "reason": reason,

        # Requirement lấy từ registry, không lấy từ LLM
        "requirements": action_config.get(
            "required_objects",
            []
        ),

        "extracted_keywords": {
            "USER": extracted_keywords.get(
                "USER"
            ),
            "GROUP": extracted_keywords.get(
                "GROUP"
            ),
            "OU": extracted_keywords.get(
                "OU"
            )
        },

        "action_tool": action_config.get(
            "action_tool"
        ),

        "action_api": action_config.get(
            "action_api"
        ),

        "required_action_group": action_config.get(
            "required_action_group"
        ),

        "confirm_required": action_config.get(
            "confirm_required",
            True
        ),

        "raw_llm_response": parsed
    }