
from app.agent.action_registry import ACTION_REGISTRY
import re



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

    pattern = re.escape(template)

    pattern = pattern.replace(
        r"\{USER\}",
        r"(?P<USER>.+?)"
    )

    pattern = pattern.replace(
        r"\{OU\}",
        r"(?P<OU>.+?)"
    )

    pattern = pattern.replace(
        r"\{GROUP\}",
        r"(?P<GROUP>.+?)"
    )

    pattern = pattern.replace(
        r"\{COMPUTER\}",
        r"(?P<COMPUTER>.+?)"
    )

    pattern = pattern.replace(
        r"\{new_value\}",
        r"(?P<new_value>.+)"
    )

    pattern = "^" + pattern + "$"

    match = re.match(
        pattern,
        user_text.strip(),
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

    user_text = user_text.strip().lower()

    for action_name, action_config in ACTION_REGISTRY.items():

        fast_commands = action_config.get(
            "fast_command",
            []
        )

        if not fast_commands:
            continue

        for command in fast_commands:

            if user_text.startswith(
                command.strip().lower()
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