import uuid


def generate_session_id() -> str:

    return (
        f"SES-"
        f"{uuid.uuid4().hex[:12].upper()}"
    )