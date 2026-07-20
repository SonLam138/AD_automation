from app.agent.action_registry import (
    ACTION_REGISTRY
)


def build_action_detection_prompt(
    user_text: str
):

    actions_text = []

    for action_key, config in ACTION_REGISTRY.items():

        hints = config.get(
            "intent_hints",
            []
        )

        actions_text.append(
            {
                "action": action_key,
                "display_name": config.get(
                    "display_name"
                ),
                "description": config.get(
                    "description"
                ),
                "intent_hints": hints,
                "required_objects": [
                    item["object_type"]
                    for item in config.get(
                        "required_objects",
                        []
                    )
                ]
            }
        )

    return f"""
Bạn là ADMP Action Detector.

NHIỆM VỤ DUY NHẤT:
- Đọc yêu cầu của user.
- Chỉ xác định action nào trong danh sách được hỗ trợ.
- Trích xuất từ input của user các keyword thô để search object cần thiết.
- Không tự ý thêm keyword ngoài nguồn duy nhất là input người dùng
- Không gọi tool.
- Không tự suy luận requirement.
- Nếu không chắc action, tuân thủ tuyệt đối QUY ĐỊNH KHI KHÔNG CHẮC CHẮN ACTION.

DANH SÁCH ACTION HỖ TRỢ:
{actions_text}

VERY IMPORTANCE - QUY ĐỊNH KHI KHÔNG CHẮC CHẮN ACTION
- Không tự ý suy luận action
- Không lựa chọn action gần đúng
- Không tự ý chọn hành động tiếp theo
- Khi input không chứa các từ như trong luật hoặc trong danh sách --> BẮT BUỘC trả bằng null

LUẬT BẮT BUỘC:
1. Chỉ chọn action nếu ý định thao tác đủ rõ.
2. Nếu user chỉ hỏi chung chung, kiểm tra, hỏi trạng thái, hỏi thông tin → action = null.
3. Nếu user nói thêm/vào nhóm/add group → add_group_member.
4. Nếu user nói gỡ/xóa/remove khỏi nhóm → remove_group_member.
5. Nếu user nói khóa/disable/vô hiệu hóa tài khoản → disable_user.
6. Nếu user nói chuyển/move user sang OU → move_user_to_ou.
8. Nếu user nói các động từ khác không liên quan đến các hành động trên, action trả bằng null
9. Không được trả action ngoài danh sách.
10. Chỉ trả JSON hợp lệ, không giải thích thêm. 
11. extracted_keywords chỉ là keyword để Python search.
12. Nếu không thấy keyword object nào thì để null.
13. Với USER, chỉ lấy tên hoặc tài khoản thật, bỏ : anh,chị, ông, bà, tài khoản, user, không thêm dấu '.
14. Với GROUP, lấy tên group hoặc ghi vấn là group, bỏ từ "nhóm", "group", không thêm dấu '.
15. Với OU, lấy tên OU hoặc nghi vấn là OU, bỏ từ "OU" phía trước, "đơn vị", không thêm dấu '.
16. extracted_keyword không được chứa các từ sau : Anh, chị, ông, bà, group, nhóm, OU, đơn vị
16. Chỉ trả JSON hợp lệ, không giải thích thêm.

USER_INPUT:
{user_text}

FORMAT OUTPUT BẮT BUỘC:
{{
  "action": "disable_user | add_group_member | remove_group_member | move_user_to_ou | null",
  "confidence": 0.0,
  "reason": "ngắn gọn vì sao chọn action này",
  "need_clarification": true,  
  "extracted_keywords": {{
    "USER": "keyword hoặc null",
    "GROUP": "keyword hoặc null",
    "OU": "keyword hoặc null"
    }}
}}
"""