import json
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
PENDING_ACTION_FILE = (
    BASE_DIR
    / "data"
    / "pending_actions.json"
)


def _load_data():
    if not PENDING_ACTION_FILE.exists():
        return {}

    with open(
        PENDING_ACTION_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def _save_data(data):
    PENDING_ACTION_FILE.parent.mkdir(
        exist_ok=True
    )

    with open(
        PENDING_ACTION_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


from datetime import datetime
import uuid


def create_pending_action(
    resolver_result: dict,
):
    data = _load_data()

    action_id = str(
        uuid.uuid4()
    )

    resolver_result["action_id"] = (
        action_id
    )

    data[action_id] = (
        resolver_result
    )

    _save_data(data)

    return action_id


def get_pending_action(
    action_id: str
):
    data = _load_data()

    return data.get(action_id)


def update_pending_action(
    action_id: str,
    payload: dict
):
    data = _load_data()

    if action_id not in data:
        return False

    data[action_id] = payload

    _save_data(data)

    return True


def delete_pending_action(
    action_id: str
):
    data = _load_data()

    if action_id not in data:
        return False

    del data[action_id]

    _save_data(data)

    return True