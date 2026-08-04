import json
import os
from datetime import datetime
from app.event.monitor_bus import (
    publish_monitor_refresh
)

RUNTIME_MONITOR_FILE = os.path.join(
    os.path.dirname(__file__),
    "runtime_monitor.json"
)


def get_today_string():
    return datetime.now().date().isoformat()


def get_now_string():
    return datetime.now().isoformat()


def build_empty_runtime_monitor():
    return {
        "date": get_today_string(),
        "total_requests": 0,
        "success_count": 0,
        "failed_count": 0,
        "last_updated": get_now_string()
    }


def load_runtime_monitor():
    """
    Load runtime monitor snapshot.

    If file is missing, empty, invalid, or belongs to another day,
    return a fresh snapshot for today.
    """

    if not os.path.exists(
        RUNTIME_MONITOR_FILE
    ):
        return build_empty_runtime_monitor()

    try:
        with open(
            RUNTIME_MONITOR_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            content = file.read().strip()

            if not content:
                return build_empty_runtime_monitor()

            data = json.loads(
                content
            )

    except Exception:
        return build_empty_runtime_monitor()

    today = get_today_string()

    if data.get("date") != today:
        return build_empty_runtime_monitor()

    return data
    # return {
    #    "date": datetime.now().strftime("%d/%m/%Y"),

    #     "total_requests": int(
    #         data.get(
    #             "total_requests",
    #             0
    #         )
    #     ),
    #     "success_count": int(
    #         data.get(
    #             "success_count",
    #             0
    #         )
    #     ),
    #     "failed_count": int(
    #         data.get(
    #             "failed_count",
    #             0
    #         )
    #     ),
    #     "last_updated": datetime.now().strftime("%H:%M")
    # }


def write_runtime_monitor(
    data: dict
):
    """
    Write runtime monitor snapshot.
    This file only keeps today's dashboard state.
    """

    data["last_updated"] = get_now_string()

    with open(
        RUNTIME_MONITOR_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    return data


def update_runtime_from_event(
    event_name: str
):
    """
    Update runtime monitor counters by runtime event name.

    Rules:
    - QUERY_RECEIVED   -> total_requests + 1
    - ACTION_COMPLETED -> success_count + 1
    - ACTION_FAILED    -> failed_count + 1

    Other events are ignored.
    """

    if event_name not in [
        "QUERY_RECEIVED",
        "ACTION_COMPLETED",
        "ACTION_FAILED"
    ]:
        return None

    data = load_runtime_monitor()

    if event_name == "QUERY_RECEIVED":
        data["total_requests"] += 1

    if event_name == "ACTION_COMPLETED":
        data["success_count"] += 1

    if event_name == "ACTION_FAILED":
        data["failed_count"] += 1

    result = write_runtime_monitor(
        data
    )

    publish_monitor_refresh()

    return result


def get_runtime_monitor_snapshot():
    """
    Return current runtime monitor snapshot for dashboard API.
    """

    data = load_runtime_monitor()

    write_runtime_monitor(
        data
    )

    return data