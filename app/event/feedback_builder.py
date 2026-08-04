import json
from pathlib import Path
from app.event.event_emitter import EVENT_LOG_FILE

def build_detection_feedback_event(
    detection_event: dict,
    user_feedback: str
):
    """
    Build training sample for Ngáo.

    Input:
        DETECTION_RESULT event
        +
        ACCEPT / REJECT

    Output:
        DETECTION_FEEDBACK event
    """

    detection_correct = (
        user_feedback.upper() == "ACCEPT"
    )

    return {
        "event_name": "DETECTION_FEEDBACK",

        "user_query": detection_event.get(
            "user_query"
        ),

        "detected_action": detection_event.get(
            "detected_action"
        ),

        "detected_keywords": detection_event.get(
            "detected_keywords",
            {}
        ),

        "user_feedback": user_feedback.upper(),

        "detection_correct": detection_correct
    }



DATASET_FILE = Path(
    "dataset/detection_feedback.jsonl"
)

def save_detection_feedback_dataset(
    feedback_event: dict
):
    DATASET_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        DATASET_FILE,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                feedback_event,
                ensure_ascii=False
            )
            + "\n"
        )

def get_detection_event_by_id(
    event_id: str
):
    if not EVENT_LOG_FILE.exists():
        return None

    with open(
        EVENT_LOG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            event = json.loads(
                line.strip()
            )

            if (
                event.get(
                    "event_name"
                )
                == "DETECTION_RESULT"
                and
                event.get(
                    "event_id"
                )
                == event_id
            ):
                return event

    return None