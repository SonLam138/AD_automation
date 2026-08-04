import os
import uuid
import json
from datetime import datetime

# Path to the JSONL file where search monitor records are appended.
# Defaults to a file named `search_monitor.jsonl` located next to this module.
SEARCH_MONITOR_FILE = os.path.join(os.path.dirname(__file__), "search_monitor.jsonl")


def get_vn_time_string():
    """Return current time as ISO format string."""
    return datetime.now().isoformat()


def write_search_record(
    username: str,
    query: str,
    action: str,
    object_type: str,
    object_name: str,
    result: str,
    metadata: dict | None = None,
    objects: list | None = None
):
    """
    Append one search monitor record to search_monitor.jsonl.

    This file is used by Monitor Search only.

    It answers:
    - ai làm
    - làm gì
    - làm với object nào
    - query input là gì
    - kết quả ra sao
    - lúc nào
    """

    record = {
        "search_id": str(uuid.uuid4()),

        "username": username,

        "query": query,

        "action": action,

        "object_type": object_type,

        "object_name": object_name,

        "objects": objects or [
            {
                "object_type": object_type,
                "object_name": object_name
            }
        ],

        "result": result,

        "time": get_vn_time_string(),

        "metadata": metadata or {}
    }

    with open(
        SEARCH_MONITOR_FILE,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False
            )
            + "\n"
        )

    return record

def load_search_records():
    """
    Load all search monitor records.
    """

    if not os.path.exists(
        SEARCH_MONITOR_FILE
    ):
        return []

    records = []

    with open(
        SEARCH_MONITOR_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:
                records.append(
                    json.loads(line)
                )

            except Exception:
                continue

    return records


def search_records(
    object_type=None,
    action_user=None,
    object_name=None,
    from_date=None,
    to_date=None
):
    records = load_search_records()

    results = []

    for record in records:

        objects = record.get(
            "objects",
            []
        ) or []

        # =====================================
        # FILTER OBJECT TYPE
        # =====================================

        if (
            object_type
            and object_type != "ALL"
        ):

            has_object_type = any(
                obj.get(
                    "object_type"
                ) == object_type
                for obj in objects
            )

            if not has_object_type:
                continue

        # =====================================
        # FILTER OBJECT NAME
        # =====================================

        if (
            object_name
            and object_name.strip()
        ):

            search_text = (
                object_name
                .strip()
                .lower()
            )

            has_object_name = any(
                search_text
                in
                str(
                    obj.get(
                        "object_name",
                        ""
                    )
                ).lower()
                for obj in objects
            )

            if not has_object_name:
                continue

        # =====================================
        # FILTER ACTION USER
        # =====================================

        if (
            action_user
            and action_user.strip()
        ):

            if (
                record.get(
                    "username",
                    ""
                ).lower()
                !=
                action_user.lower()
            ):
                continue

        # =====================================
        # FILTER DATE RANGE
        # =====================================

        record_time = (
            record.get(
                "time",
                ""
            )[:10]
        )

        if (
            from_date
            and record_time < from_date
        ):
            continue

        if (
            to_date
            and record_time > to_date
        ):
            continue

        results.append(
            record
        )

    return results