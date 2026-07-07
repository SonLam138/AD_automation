import json
from pathlib import Path


AUDIT_ROOT = (
    Path(__file__).resolve().parent
    / "audit_data"
)


SESSION_CONTEXT_DIR = (
    AUDIT_ROOT / "session_context"
)

SESSION_STEPS_DIR = (
    AUDIT_ROOT / "session_steps"
)

SUMMARY_DIR = (
    AUDIT_ROOT / "operational_summary"
)


from datetime import datetime


def json_serializer(obj):

    if isinstance(
        obj,
        datetime
    ):
        return obj.isoformat()

    raise TypeError(
        f"Type {type(obj)} not serializable"
    )


def write_json(
    path,
    data
):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
            default=json_serializer
        )


def ensure_audit_folders():

    SESSION_CONTEXT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SESSION_STEPS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SUMMARY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def to_dict(obj):

    if isinstance(obj, dict):
        return obj

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    if hasattr(obj, "dict"):
        return obj.dict()

    raise TypeError(
        f"Unsupported audit type: {type(obj)}"
    )


def save_context(
    context
):

    ensure_audit_folders()

    context_data = to_dict(
        context
    )

    session_id = context_data[
        "session_id"
    ]

    file_path = (
        SESSION_CONTEXT_DIR
        / f"{session_id}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            context_data,
            f,
            indent=2,
            ensure_ascii=False,
            default=json_serializer
        )

    print(
        f"[AUDIT] Context saved: {file_path}"
    )


def save_step(step):

    ensure_audit_folders()

    step_data = to_dict(step)

    session_id = step_data["session_id"]

    file_path = (
        SESSION_STEPS_DIR
        / f"{session_id}.jsonl"
    )

    with open(
        file_path,
        "a",
        encoding="utf-8"
    ) as f:

        json.dump(
            step_data,
            f,
            ensure_ascii=False,
            default=json_serializer
        )

        f.write("\n")

    print(
        f"[AUDIT] Step saved: {step_data['step_name']}"
    )

def save_summary(summary):

    ensure_audit_folders()

    summary_data = to_dict(
        summary
    )

    session_id = summary_data[
        "session_id"
    ]

    file_path = (
        SUMMARY_DIR
        / f"{session_id}.json"
    )

    write_json(
        file_path,
        summary_data
    )

    print(
        f"[AUDIT] Summary saved: "
        f"{session_id}"
    )