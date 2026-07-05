import json
from pathlib import Path

PENDING_REQUEST_FILE = Path(
    f"D:\\AD Automation\\app\\data\\pending_requests.json"
)

def load_pending_requests():

    if not PENDING_REQUEST_FILE.exists():
        return []

    with open(
        PENDING_REQUEST_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
def save_pending_requests(
    requests
):

    with open(
        PENDING_REQUEST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            requests,
            f,
            ensure_ascii=False,
            indent=2
        )


def add_pending_request(
    request_data
):

    requests = load_pending_requests()

    requests.append(
        request_data
    )

    save_pending_requests(
        requests
    )

def get_pending_requests():

    requests = load_pending_requests()

    return [
        r
        for r in requests
        if r["status"] == "PENDING"
    ]

def get_pending_request_by_id(
    request_id: str
):

    requests = load_pending_requests()

    for request in requests:

        if request["request_id"] == request_id:
            return request

    return None

def update_request_status(
    request_id: str,
    status: str
):

    requests = load_pending_requests()

    for request in requests:

        if request["request_id"] == request_id:

            request["status"] = status

            save_pending_requests(
                requests
            )

            return request

    return None

def remove_pending_request(
    request_id: str
):

    requests = load_pending_requests()

    requests = [
        r
        for r in requests
        if r["request_id"] != request_id
    ]

    save_pending_requests(
        requests
    )
