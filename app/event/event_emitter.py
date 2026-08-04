import json
import uuid
from datetime import datetime
from pathlib import Path
from app.event.runtime_bus import publish_event
from Monitor.monitor_consumer import consume_monitor_event

EVENT_LOG_FILE = (
    Path("logs") / "events.jsonl"
)


def emit_event(**event_data):
    EVENT_LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    event_data.setdefault(
        "event_id",
        str(uuid.uuid4())
    )

    event_data.setdefault(
        "timestamp",
        datetime.utcnow().isoformat()
    )

    event = dict(
        event_data
    )

    with open(
        EVENT_LOG_FILE,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            json.dumps(
                event,
                ensure_ascii=False
            )
            + "\n"
        )

    try:
        consume_monitor_event(
            event
        )

    except Exception as ex:
        print(
            "MONITOR CONSUMER ERROR =",
            ex
        )

    try:
        publish_event(
            event
        )

        print(
            "RUNTIME BUS PUBLISH =",
            event.get(
                "event_name"
            )
        )

    except Exception as ex:
        print(
            "RUNTIME BUS ERROR =",
            ex
        )

    return event