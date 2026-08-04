import json
import os
from datetime import datetime

MONITOR_FILE = os.path.join(
    "Monitor",
    "runtime_monitor.json"
)


def write_runtime_record(
    total_requests: int,
    success_count: int,
    failed_count: int
):
    data = {
        "total_requests": total_requests,
        "success_count": success_count,
        "failed_count": failed_count,
        "last_updated": datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )
    }

    with open(
        MONITOR_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )