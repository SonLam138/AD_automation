
from app.agent.action_registry import ACTION_REGISTRY
import re
import unicodedata

def normalize_text(
    text: str
):
    if not text:
        return ""

    text = text.lower().strip()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        c
        for c in text
        if unicodedata.category(c) != "Mn"
    )

    text = text.replace(
        "đ",
        "d"
    )

    return text


def parse_fast_command(
    template: str,
    user_text: str
):
    """
    Convert:

    Tôi cần disable user {USER}

    thành

    Tôi cần disable user (?P<USER>.+)

    """

    normalized_template = normalize_text(
        template
    )

    pattern = re.escape(
        normalized_template
    )

    pattern = pattern.replace(
        r"\{user\}",
        r"(?P<USER>.+?)"
    )

    pattern = pattern.replace(
        r"\{ou\}",
        r"(?P<OU>.+?)"
    )

    pattern = pattern.replace(
        r"\{group\}",
        r"(?P<GROUP>.+?)"
    )

    pattern = pattern.replace(
        r"\{computer\}",
        r"(?P<COMPUTER>.+?)"
    )

    pattern = pattern.replace(
        r"\{new_value\}",
        r"(?P<new_value>.+)"
    )

    pattern = "^" + pattern + "$"

    #normalized_pattern = normalize_text(pattern)

    normalized_user_text = normalize_text(
        user_text
    )

    match = re.match(
    pattern,
    normalized_user_text,
    re.IGNORECASE
)

    if not match:
        return None

    return match.groupdict()


def detect_fast_command(
    user_text: str
):
    """
    Detect fast command from ACTION_REGISTRY.

    Return:

    {
        "action": "...",
        "action_config": {...}
    }

    or None
    """

    if not user_text:
        return None

    normalized_user_text = normalize_text(
        user_text
    )

    for action_name, action_config in ACTION_REGISTRY.items():

        fast_commands = action_config.get(
            "fast_command",
            []
        )

        if not fast_commands:
            continue

        for command in fast_commands:

            normalized_command = normalize_text(
                command
            )

            if normalized_user_text.startswith(
                normalized_command
            ):

                return {
                    "action": action_name,
                    "action_config": action_config
                }

    return None


def extract_keywords(
    action_config,
    user_text: str
):
    """
    Extract keywords from kw_template.

    Return:

    {
        "USER": "...",
        "GROUP": "...",
        ...
    }

    or {}
    """

    kw_templates = action_config.get(
        "kw_template",
        []
    )

    if not kw_templates:
        return {}

    for template in kw_templates:

        variables = parse_fast_command(
            template=template,
            user_text=user_text
        )

        if variables:
            return variables

    return {}




if __name__ == "__main__":

    result = detect_fast_command(
        "Tôi cần thay đổi displayname SonNM thành SVD ID new"
    )

    print(result)