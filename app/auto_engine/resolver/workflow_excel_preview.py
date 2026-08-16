from typing import (
    Any,
    Dict,
    List,
)

from app.adapters.ldap_container import (
    ldap
)

from app.search_tools.workflow_search_user import (
    workflow_search_user
)
from datetime import (
    datetime,
    timezone,
)

from uuid import (
    uuid4
)

# ==================================================
# PREVIEW STATUS
# ==================================================

STATUS_VALID = "VALID"

STATUS_MISSING_IDENTITY = (
    "MISSING_IDENTITY"
)

STATUS_MISSING_REASON = (
    "MISSING_REASON"
)

STATUS_MISSING_EFFECTIVE_TIME = (
    "MISSING_EFFECTIVE_TIME"
)

STATUS_NOT_FOUND = (
    "NOT_FOUND"
)

STATUS_MULTIPLE_MATCH = (
    "MULTIPLE_MATCH"
)

STATUS_ALREADY_DISABLED = (
    "ALREADY_DISABLED"
)

STATUS_LOOKUP_FAILED = (
    "LOOKUP_FAILED"
)

# ==================================================
# CREATE REVIEW SESSION ID
# ==================================================

def create_review_session_id() -> str:

    timestamp = (
        datetime
        .now(
            timezone.utc
        )
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    random_part = (
        uuid4()
        .hex[:8]
        .upper()
    )

    return (
        f"REVIEW_{timestamp}_{random_part}"
    )


# ==================================================
# NORMALIZE VALUE
# ==================================================

def _normalize_value(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(
        value
    ).strip()


# ==================================================
# BUILD REVIEW ROW
# ==================================================

def _build_base_review_row(
    row_number: int,
    row: Dict[str, Any],
) -> Dict[str, Any]:

    return {
        "row_number":
            row_number,

        "employee_id":
            _normalize_value(
                row.get(
                    "employee_id"
                )
            ),

        "email":
            _normalize_value(
                row.get(
                    "email"
                )
            ),

        "reason":
            _normalize_value(
                row.get(
                    "reason"
                )
            ),

        "effective_time":
            _normalize_value(
                row.get(
                    "effective_time"
                )
            ),

        "status":
            None,

        "message":
            None,

        "display_name":
            None,

        "sam_account_name":
            None,

        "is_disabled":
            None,
    }


# ==================================================
# REVIEW ONE OFFBOARDING ROW
# ==================================================

def review_offboarding_row(
    row_number: int,
    row: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Resolve và validate một dòng Offboarding.

    Không tạo Request.
    Không generate ExecutionPlan.
    Không chạy Job.
    Không thay đổi dữ liệu AD.
    """

    review_row = (
        _build_base_review_row(
            row_number=row_number,
            row=row,
        )
    )

    employee_id = (
        review_row[
            "employee_id"
        ]
    )

    email = (
        review_row[
            "email"
        ]
    )

    reason = (
        review_row[
            "reason"
        ]
    )

    effective_time = (
        review_row[
            "effective_time"
        ]
    )

    # ==============================================
    # REQUIRED BUSINESS DATA
    # ==============================================

    if (
        not employee_id
        and
        not email
    ):

        review_row["status"] = (
            STATUS_MISSING_IDENTITY
        )

        review_row["message"] = (
            "Thiếu Employee ID hoặc Email."
        )

        return review_row

    if not reason:

        review_row["status"] = (
            STATUS_MISSING_REASON
        )

        review_row["message"] = (
            "Thiếu lý do Offboarding."
        )

        return review_row

    if not effective_time:

        review_row["status"] = (
            STATUS_MISSING_EFFECTIVE_TIME
        )

        review_row["message"] = (
            "Thiếu thời điểm có hiệu lực."
        )

        return review_row

    # ==============================================
    # EXACT AD LOOKUP
    # ==============================================

    try:

        search_result = (
            workflow_search_user(
                connection=
                    ldap.connection,

                employee_id=
                    employee_id
                    or None,

                email=
                    email
                    or None,
            )
        )

    except Exception as exc:

        review_row["status"] = (
            STATUS_LOOKUP_FAILED
        )

        review_row["message"] = (
            f"Không thể tra cứu AD: {exc}"
        )

        return review_row

    # ==============================================
    # LDAP SEARCH FAILED
    # ==============================================

    if not search_result.get(
        "success",
        False,
    ):

        review_row["status"] = (
            STATUS_LOOKUP_FAILED
        )

        review_row["message"] = (
            search_result.get(
                "message"
            )
            or
            "Tra cứu AD không thành công."
        )

        return review_row

    result_count = (
        search_result.get(
            "count",
            0,
        )
    )

    # ==============================================
    # NO USER FOUND
    # ==============================================

    if result_count == 0:

        review_row["status"] = (
            STATUS_NOT_FOUND
        )

        review_row["message"] = (
            "Không tìm thấy tài khoản "
            "khớp chính xác trên AD."
        )

        return review_row

    # ==============================================
    # MORE THAN ONE USER - FAIL CLOSED
    # ==============================================

    if result_count > 1:

        review_row["status"] = (
            STATUS_MULTIPLE_MATCH
        )

        review_row["message"] = (
            "Tìm thấy nhiều hơn một tài khoản. "
            "Dòng này đã bị dừng xử lý."
        )

        return review_row

    # Đến đây count chắc chắn bằng 1.
    user = (
        search_result[
            "results"
        ][0]
    )

    review_row[
        "display_name"
    ] = user.get(
        "display_name"
    )

    review_row[
        "sam_account_name"
    ] = user.get(
        "sam_account_name"
    )

    review_row[
        "is_disabled"
    ] = user.get(
        "is_disabled"
    )

    # Hiển thị identity thật lấy từ AD.
    review_row[
        "resolved_employee_id"
    ] = user.get(
        "employee_id"
    )

    review_row[
        "resolved_email"
    ] = user.get(
        "mail"
    )

    # ==============================================
    # ALREADY DISABLED
    # ==============================================

    if user.get(
        "is_disabled"
    ) is True:

        review_row["status"] = (
            STATUS_ALREADY_DISABLED
        )

        review_row["message"] = (
            "Tài khoản đã bị disable. "
            "Không đủ điều kiện tạo "
            "Offboarding Request mới."
        )

        return review_row

    # ==============================================
    # VALID
    # ==============================================

    review_row["status"] = (
        STATUS_VALID
    )

    review_row["message"] = (
        "Dữ liệu hợp lệ và tài khoản "
        "đang active trên AD."
    )

    return review_row


# ==================================================
# REVIEW ALL OFFBOARDING ROWS
# ==================================================

def review_offboarding_rows(
    rows: List[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:
    """
    Review toàn bộ dữ liệu Excel đã được normalize.

    row_number bắt đầu từ 2 vì dòng 1 là header Excel.
    """

    review_rows = []

    for index, row in enumerate(
        rows,
        start=2,
    ):

        review_rows.append(
            review_offboarding_row(
                row_number=index,
                row=row,
            )
        )

    valid_rows = sum(
        1
        for row in review_rows
        if row["status"] == STATUS_VALID
    )

    invalid_rows = (
        len(review_rows)
        -
        valid_rows
    )

    can_confirm = (
        len(review_rows) > 0
        and
        invalid_rows == 0
    )

    request_candidates = []

    for row in review_rows:

        if row["status"] == "VALID":

            request_candidates.append({

                "employee_id":
                    row["employee_id"],

                "email":
                    row["email"],

                "reason":
                    row["reason"],

                "effective_time":
                    row["effective_time"]
            })


    return {
        "success":
            True,

        "total_rows":
            len(review_rows),

        "valid_rows":
            valid_rows,

        "invalid_rows":
            invalid_rows,

        "can_confirm":
            can_confirm,

        "rows":
            review_rows,
        "request_candidates":
            request_candidates
    }