import json
from app.agent.llm_client import ask_llm

def build_execution_prompt(
    execution_contract: dict
):

    contract_json = json.dumps(
        execution_contract,
        ensure_ascii=False,
        indent=2
    )

    return f"""
Bạn là ADMP Execution Response Planner.

NHIỆM VỤ

- Đọc execution contract.
- Thông báo kết quả cho người dùng.
- Không yêu cầu xác nhận.
- Không hỏi Y/N.
- Không đề xuất thao tác tiếp theo nếu không cần thiết.
- Không suy luận ngoài contract.

==================================================
EXECUTION CONTRACT
==================================================

{contract_json}

==================================================
LUẬT XỬ LÝ
==================================================

1. Nếu state = ACTION_SUCCESS

→ Thông báo thao tác thành công.
→ Tóm tắt ngắn gọn kết quả.
→ Ngôn ngữ thân thiện và chuyên nghiệp.

2. Nếu state = ACTION_FAILED

→ Thông báo thao tác thất bại.
→ Nêu ngắn gọn lỗi nếu có.

==================================================
QUY ĐỊNH OUTPUT
==================================================

- Chỉ trả về nội dung hội thoại.
- Không trả JSON.
- Không trả code block.
- Không trả field message.
- Không trả field response.
- Không hiển thị DN

==================================================
NGÔN NGỮ
==================================================

- Luôn trả lời bằng tiếng Việt.
"""

def generate_execution_response(
    execution_contract: dict
):

    prompt = build_execution_prompt(
        execution_contract
    )

    response = ask_llm(
        prompt
    )

    try:

        data = json.loads(response)

        return (
            data.get("text")
            or response
        )

    except Exception:

        return response.strip()