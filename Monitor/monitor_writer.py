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