import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


APP_DIR = Path(__file__).resolve().parents[2]

DEFAULT_PENDING_FILE = (
    APP_DIR
    / "data"
    / "pending_requests.json"
)


def now_iso() -> str:
    return datetime.now().isoformat(
        timespec="microseconds"
    )


def create_request_id() -> str:
    return "REQ-" + uuid.uuid4().hex[:8].upper()


def _get_nested(
    data: Dict[str, Any],
    *keys,
    default=None
):
    current = data

    for key in keys:
        if not isinstance(current, dict):
            return default

        current = current.get(key)

        if current is None:
            return default

    return current


def build_pending_request_from_resolver_result(
    resolver_result: Dict[str, Any],
    request_id: str = None
) -> Dict[str, Any]:
    """
    Build Pending Request V2 từ output thật của Resolver V2.

    Input resolver_result expected structure:

    {
      "extract_result": {
        "employee_extract": {...}
      },
      "lookup_result": {...},
      "final_result": {
        "resolved_data": {...}
      }
    }

    Pending Request chỉ chứa thông tin reviewer cần review,
    không chứa thông tin kỹ thuật như task_type, tool, confidence.
    """

    request_id = request_id or create_request_id()

    employee_extract = _get_nested(
        resolver_result,
        "extract_result",
        "employee_extract",
        default={}
    )

    resolved_data = _get_nested(
        resolver_result,
        "final_result",
        "resolved_data",
        default={}
    )

    # Fallback nhẹ nếu final_result bị parse khác cấu trúc
    if not resolved_data and isinstance(
        resolver_result.get("final_result"),
        dict
    ):
        resolved_data = resolver_result["final_result"].get(
            "resolved_data",
            {}
        )

    pending_request = {
        "request_id": request_id,

        "status": "PENDING",

        "created_at": now_iso(),

        "hr_input": {
            "employee_id": employee_extract.get(
                "employee_id",
                resolved_data.get("employee_id", "")
            ),

            "full_name": employee_extract.get(
                "full_name",
                resolved_data.get("name", "")
            ),

            "birth_date": employee_extract.get(
                "birth_date",
                ""
            ),

            "title": employee_extract.get(
                "title",
                resolved_data.get("title", "")
            ),

            "position": employee_extract.get(
                "position",
                employee_extract.get(
                    "title",
                    resolved_data.get("title", "")
                )
            ),

            "department": employee_extract.get(
                "org_line",
                resolved_data.get("department_name", "")
            ),

            "division": employee_extract.get(
                "division_name",
                ""
            )
        },

        "resolved_result": {
            "firstname": resolved_data.get(
                "first_name",
                ""
            ),

            "lastname": resolved_data.get(
                "last_name",
                ""
            ),

            "sam_account_name": (
                resolved_data.get("sam_account_name")
                or resolved_data.get("requested_account")
                or ""
            ),

            "display_name": resolved_data.get(
                "display_name",
                ""
            ),

            "title": resolved_data.get(
                "title",
                ""
            ),

            "department": resolved_data.get(
                "department_name",
                ""
            ),

            "target_ou_dn": resolved_data.get(
                "target_ou",
                ""
            ),

            "groups": (
                [resolved_data["group_name"]]
                if resolved_data.get("group_name")
                else []
            )
        }
    }

    return pending_request


def load_pending_requests(
    file_path: Path = DEFAULT_PENDING_FILE
) -> List[Dict[str, Any]]:
    if not file_path.exists():
        return []

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    # Nếu lỡ file cũ là object đơn
    if isinstance(data, dict):
        return [data]

    return []


def save_pending_requests(
    pending_requests: List[Dict[str, Any]],
    file_path: Path = DEFAULT_PENDING_FILE
) -> None:
    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            pending_requests,
            f,
            ensure_ascii=False,
            indent=2
        )


def upsert_pending_request(
    pending_request: Dict[str, Any],
    file_path: Path = DEFAULT_PENDING_FILE
) -> None:
    """
    Ghi pending request vào file JSON.

    Nếu request_id đã tồn tại thì update.
    Nếu chưa có thì append.
    """

    pending_requests = load_pending_requests(
        file_path
    )

    request_id = pending_request["request_id"]

    updated = False

    for index, item in enumerate(pending_requests):
        if item.get("request_id") == request_id:
            pending_requests[index] = pending_request
            updated = True
            break

    if not updated:
        pending_requests.append(
            pending_request
        )

    save_pending_requests(
        pending_requests,
        file_path
    )


if __name__ == "__main__":
    sample_resolver_result = {
        "extract_result": {
            "employee_extract": {
                "full_name": "Dương Anh Tuấn",
                "employee_id": "00017005",
                "title": "Trưởng Bộ phận khách hàng doanh nghiệp siêu nhỏ",
                "org_line": "PVcomBank Tây Lộc - Phòng Khách Hàng Cá Nhân - Bộ Phận Khách Hàng Doanh Nghiệp Siêu Nhỏ"
            }
        },
        "final_result": {
            "resolved_data": {
                "firstname": "Tuấn",
                "lastname": "Dương Anh",
                "name": "Dương Anh Tuấn",
                "display_name": "Dương Anh Tuấn (TLC)",
                "employee_id": "00017005",
                "title": "Trưởng Bộ phận khách hàng doanh nghiệp siêu nhỏ",
                "department_name": "Phòng Khách Hàng Cá Nhân - Bộ Phận Khách Hàng Doanh Nghiệp Siêu Nhỏ",
                "target_ou": "OU=PVCB Tay Loc,OU=CN-Azure,OU=Chi nhanh,DC=pvcb,DC=vn",
                "member_of": [
                    "tayloc.khcn"
                ]
            }
        }
    }

    pending = build_pending_request_from_resolver_result(
        sample_resolver_result
    )

    print(
        json.dumps(
            pending,
            ensure_ascii=False,
            indent=2
        )
    )