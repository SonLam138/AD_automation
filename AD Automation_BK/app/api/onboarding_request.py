from fastapi import APIRouter, Body

from app.storage.pending_requests import (
    get_pending_requests,
    get_pending_request_by_id
)
from app.storage.pending_requests import (
    load_pending_requests,
    save_pending_requests
)
from app.storage.pending_requests import (
    update_request_status
)
from app.storage.pending_requests import (
    remove_pending_request
)
router = APIRouter()

#  API lấy danh sách pending
@router.get("/pending")
def get_pending_request_list():

    return get_pending_requests()

# API lấy chi tiết request theo request_id
@router.get("/{request_id}")
def get_request_detail(
    request_id: str
):

    request = get_pending_request_by_id(
        request_id
    )

    if request is None:

        return {
            "success": False,
            "message": "Request not found"
        }

    return request

#  API cập nhật request pending
@router.put("/{request_id}")
def update_request(
    request_id: str,
    payload: dict = Body(...)
):

    requests = load_pending_requests()

    for request in requests:

        if request["request_id"] == request_id:

            request["resolved_result"] = payload[
                "resolved_result"
            ]

            save_pending_requests(
                requests
            )

            return request

    return {
        "success": False,
        "message": "Request not found"
    }

#  API refject request pending and remove from pending list
@router.post("/{request_id}/reject")
def reject_request(
    request_id: str
):

    remove_pending_request(
        request_id
    )

    return {
        "success": True,
        "request_id": request_id,
        "action": "REJECTED"
    }