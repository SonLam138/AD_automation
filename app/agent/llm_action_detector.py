import json
import re

from app.agent.action_prompt import (
    build_action_detection_prompt
)

from app.agent.action_registry import (
    ACTION_REGISTRY
)

from app.agent.llm_action_detector_bk import detect_action_by_llm
from app.agent.llm_client import (
    ask_llm
)
from app.agent.fast_command_detector import (
    detect_fast_command,
    extract_keywords
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

def detect_action(
    user_text: str
):
    fast_result = detect_fast_command(
    user_text
    )

    if fast_result:

        variables = extract_keywords(
            action_config=fast_result[
                "action_config"
            ],
            user_text=user_text
        )

        extracted_keywords = {}

        for key, value in variables.items():

            if key == "new_value":
                continue

            extracted_keywords[key] = value

        return build_detect_result(
            action=fast_result["action"],

            action_config=fast_result[
                "action_config"
            ],

            extracted_keywords=
                extracted_keywords,

            confidence=1.0,

            reason=
                "Fast command matched",

            new_value=variables.get(
                "new_value"
            ),

            source="fast_command",

            raw_response={
                "fast_result": fast_result,
                "variables": variables
            }
        )
    
    return detect_action_by_llm(user_text=user_text)



def build_detect_result(
    action: str,
    extracted_keywords: dict,
    action_config: dict,
    confidence: float = 1.0,
    reason: str = "",
    new_value: str = None,
    source: str = "llm",
    raw_response=None
):
    return {
    "success": True,

    "status":
        "ACTION_DETECTED",

    "action":
        action,

    "display_name":
        action_config.get(
            "display_name"
        ),

    "confidence":
        confidence,

    "reason":
        reason,

    "requirements":
        action_config.get(
            "required_objects",
            []
        ),

    "extracted_keywords":
        extracted_keywords,

    "new_value":
        new_value,

    "action_tool":
        action_config.get(
            "action_tool"
        ),

    "action_api":
        action_config.get(
            "action_api"
        ),

    "required_action_group":
        action_config.get(
            "required_action_group"
        ),

    "confirm_required":
        action_config.get(
            "confirm_required",
            True
        ),

    "source":
        source,

    "raw_llm_response":
        raw_response
    }




def detect_action_by_llm(
    user_text: str
):
    """
    LLM Action Detector.

    Responsibility:
    - Ask LLM to detect action
    - Validate action
    - Validate confidence
    - Load action metadata from ACTION_REGISTRY

    Important:
    - Requirements are loaded from registry.
    - Search is NOT performed here.
    - LDAP action is NOT performed here.
    - extracted_keywords must be passed through as-is.
    - Object types must NOT be hard-coded here.
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
    print(parsed)
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

    need_clarification = parsed.get(
        "need_clarification",
        False
    )

    extracted_keywords = parsed.get(
        "extracted_keywords",
        {}
    )

    if not isinstance(
        extracted_keywords,
        dict
    ):
        extracted_keywords = {}

    new_value = parsed.get("new_value")


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

    return build_detect_result(
        action=action,
        extracted_keywords=extracted_keywords,
        action_config=action_config,
        confidence=confidence,
        reason=reason,
        new_value=new_value,
        source="llm",
        raw_response=parsed
    )