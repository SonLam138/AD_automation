import random


# ==================================================
# OBJECT TYPE LABELS
# ==================================================

OBJECT_TYPE_LABELS = {
    "USER": "tài khoản người dùng",
    "GROUP": "nhóm",
    "COMPUTER": "máy tính",
    "OU": "OU"
}


def _get_object_label(
    object_type: str
) -> str:

    if not object_type:
        return "đối tượng"

    return OBJECT_TYPE_LABELS.get(
        object_type,
        object_type
    )


# ==================================================
# MISSING KEYWORD MESSAGE
# ==================================================

MISSING_KEYWORD_MESSAGES = [
    "Ngáo chưa xác định được đối tượng cần xử lý.",
    "Em chưa thấy thông tin đối tượng trong yêu cầu này.",
    "Ngáo cần thêm một chút thông tin để tìm đúng đối tượng.",
    "Em chưa đủ dữ liệu để xác định đối tượng cần thao tác."
]


def build_missing_keyword_message(
    object_type: str
) -> str:

    object_label = _get_object_label(
        object_type
    )

    return (
        f"{random.choice(MISSING_KEYWORD_MESSAGES)} "
        f"Anh bổ sung giúp em thông tin {object_label} nhé."
    )


# ==================================================
# NOT FOUND MESSAGE
# ==================================================

NOT_FOUND_MESSAGES = [
    "Ngáo chưa tìm thấy đối tượng phù hợp.",
    "Em chưa tìm được kết quả nào khớp với thông tin anh cung cấp.",
    "Hiện tại Ngáo chưa xác định được đối tượng tương ứng trong Active Directory.",
    "Em đã tìm thử nhưng chưa thấy đối tượng phù hợp."
]


def build_not_found_message(
    result: dict
) -> str:

    target_object_type = result.get(
        "target_object_type"
    )

    object_label = _get_object_label(
        target_object_type
    )

    return (
        f"{random.choice(NOT_FOUND_MESSAGES)} "
        f"Anh kiểm tra lại thông tin {object_label} hoặc cung cấp thêm dữ liệu giúp em nhé."
    )


# ==================================================
# NEED OBJECT SELECTION MESSAGE
# ==================================================

OBJECT_SELECTION_MESSAGES = [
    "Ngáo tìm thấy nhiều đối tượng phù hợp.",
    "Có một vài kết quả đang khớp với yêu cầu của anh.",
    "Em tìm được nhiều đối tượng có thể là đối tượng cần thao tác.",
    "Ngáo chưa đủ chắc chắn để tự chọn một đối tượng duy nhất."
]


def _count_candidate_objects(
    result: dict
) -> int:

    candidate_objects = result.get(
        "candidate_objects",
        {}
    )

    total = 0

    for items in candidate_objects.values():

        if isinstance(
            items,
            list
        ):
            total += len(
                items
            )

    return total


def build_object_selection_message(
    result: dict
) -> str:

    count = _count_candidate_objects(
        result
    )

    if count > 0:
        return (
            f"{random.choice(OBJECT_SELECTION_MESSAGES)} "
            f"Hiện có {count} đối tượng cần anh xác nhận lại, "
            f"anh chọn giúp em đối tượng chính xác nhé."
        )

    return (
        f"{random.choice(OBJECT_SELECTION_MESSAGES)} "
        f"Anh chọn giúp em đối tượng chính xác nhé."
    )


# ==================================================
# CONFIRM READY MESSAGE
# ==================================================

CONFIRM_READY_MESSAGES = [
    "Ngáo đã xác định được đối tượng cần xử lý.",
    "Em đã chuẩn bị xong thông tin xác nhận.",
    "Thông tin cần thiết đã sẵn sàng.",
    "Ngáo đã hoàn tất bước đối chiếu thông tin.",
    "Em đã tìm thấy đối tượng phù hợp và chuẩn bị xong thao tác."
]


def _get_primary_resolved_object(
    result: dict
) -> dict:

    resolved_objects = result.get(
        "resolved_objects",
        {}
    )

    for value in resolved_objects.values():

        if isinstance(
            value,
            dict
        ):
            return value

    return {}


def _get_object_display_name(
    obj: dict
) -> str:

    if not obj:
        return ""

    return (
        obj.get("sam_account_name")
        or obj.get("display_name")
        or obj.get("computer_name")
        or obj.get("dns_host_name")
        or obj.get("group_name")
        or obj.get("name")
        or ""
    )


def build_confirm_ready_message(
    result: dict
) -> str:

    obj = _get_primary_resolved_object(
        result
    )

    object_name = _get_object_display_name(
        obj
    )

    if object_name:
        return (
            f"{random.choice(CONFIRM_READY_MESSAGES)} "
            f"Đối tượng: {object_name}. "
            f"Anh kiểm tra lại thông tin trước khi thực hiện giúp em nhé."
        )

    return (
        f"{random.choice(CONFIRM_READY_MESSAGES)} "
        f"Anh kiểm tra lại thông tin trước khi thực hiện giúp em nhé."
    )


# ==================================================
# MAIN RESOLVER MESSAGE
# ==================================================

def build_resolver_message(
    result: dict
) -> str:

    status = result.get(
        "status"
    )

    state = result.get(
        "state"
    )

    if (
        status == "NOT_FOUND"
        or state == "WAITING_REQUIRED_OBJECT"
    ):
        return build_not_found_message(
            result
        )

    if status == "NEED_OBJECT_SELECTION":
        return build_object_selection_message(
            result
        )

    if state == "WAITING_OBJECT_SELECTION":
        return build_object_selection_message(
            result
        )

    if (
        status == "READY_TO_CONFIRM"
        or state == "CONFIRM_READY"
    ):
        return build_confirm_ready_message(
            result
        )

    return ""

