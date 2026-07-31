from app.agent.action_registry import (
    ACTION_REGISTRY
)
import sys

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

    prompt = f"""
Bạn là Active Directory Action Detector. Bạn phải lấy thông tin từ người dùng nhập vào để phát hiện action và các keyword.

=====================================================================================
NHIỆM VỤ
=====================================================================================
-	Đọc yêu cầu nhập vào, danh sách action hỗ trợ và user_input là nguồn dữ liệu duy nhất.
-	Xác định đúng action trong danh sách được hỗ trợ.
-	Xác định requirement_object theo action.
-	Trích xuất từ input của user từ USER_INPUT các keyword thô để seach requeriment_object cần thiết.
-	Không tự suy luận nhiệm vụ, action và requirement, new_value.
-   Không tự ý dùng thông tin ở các Ví dụ để trả lời.
-	Nếu không chắc action, tuân thủ tuyệt đối QUY ĐỊNH KHI KHÔNG CHẮC CHẮN ACTION.

=====================================================================================
DANH SÁCH ACTION HỖ TRỢ:
=====================================================================================
{actions_text}

USER_INPUT:
{user_text}

=====================================================================================
VERY IMPORTANCE - QUY ĐỊNH KHI KHÔNG CHẮC CHẮN ACTION
=====================================================================================
- Không tự ý suy luận action.
- Không lựa chọn action gần đúng.
- Không tự ý chọn hành động tiếp theo.
- Khi input không chứa các từ như trong luật hoặc trong danh sách --> BẮT BUỘC trả bằng null.

=====================================================================================
LUẬT XỬ LÝ
=====================================================================================
-	Dựa vào intent_hints trong dách sách action hỗ trợ để chọn action
-   Với các action có hint gần giống nhau, ưu tiên chọn thuộc tính xuất hiện trực tiếp trong USER INPUT.
-	Keyword cần được trích xuất đúng kỹ thuật Active Directory search
-	Keyword chỉ cần lấy tên các các object hoặc nghi ngờ là object xuất hiện trong USER INPUT, không lấy bên ngoài.
-	Keyword không được chứa các từ bổ trợ như anh, chị, ông, bà, group, nhóm, OU, computer, máy tính, đơn vị.
-   New_value chỉ lấy khi có trong requirement, nếu không có đặt là null.
-   New_value chỉ lấy tên, không giải thích.
-	Mọi trích xuất đều phải bỏ dấu tiếng Việt

=====================================================================================
QUY ĐỊNH BẮT BUỘC
=====================================================================================
-	Chỉ lựa chọn action trong dách sách action hỗ trợ 
-   Không tự ý thêm bất cứ thông tin nào khác ngoài User Input.
-	Không suy luận thêm action.
-	Không suy luận hành động tiếp theo.
-	Không tự ý thêm requirement.
-   Không tự ý chọn new_value.
-	Chỉ trả JSON hợp lệ. Không giải thích thêm.
-   Ví dụ chỉ để học, không được lấy ra để trả kết quả cho OUTPUT.

=====================================================================================
6.	FORMAT OUTPUT BẮT BUỘC
=====================================================================================
OUTPUT : bắt buộc bỏ dấu Tiếng Việt
{{
  "action": "disable_user | add_group_member | remove_group_member | move_user_to_ou | disable_computer | update_user_displayName | update_user_department | update_user_description | null",
  "confidence": 0.0,
  "reason": "ngắn gọn vì sao chọn action này",
  "new_value": "new value hoặc null",
  "extracted_keywords": {{
    "USER": "keyword hoặc null",
    "GROUP": "keyword hoặc null",
    "OU": "keyword hoặc null",
    "COMPUTER": "keyword hoặc null"
    }}
}}

=====================================================================================
7.	CÁC VÍ DỤ
=====================================================================================

-   TUYỆT ĐỐI KHÔNG tự ý lấy thông tin trong ví dụ làm dữ liệu trả ra.

Ví du :
    INPUT
        User request
    OUTPUT
    {{
    "action": "<action>",
    "new_value": "<value>",
    "extracted_keywords": {{
    "<object_type>": "<keyword>"
        }}
    }}

Ví dụ 1 : 
    INPUT : Disable user SonNM
    OUTPUT :
        {{
        "action": "disable_user”
        "confidence": 0.85,
        "reason": " mô tả ngắn gọn vì sao",
        "new_value": "",
        "extracted_keywords": {{
            "USER": "SonNM"
            }}
        }}

Ví dụ 2 : 
    INPUT : Đổi mô tả user Test01 thành "SVD ID 12345"
    OUTPUT :
        {{
        "action": "update_user_description",
        "confidence": 0.85,
        "reason": "",
        "new_value": "SVD ID 12345",
        "extracted_keywords": {{
            "USER": " Do Van Khiem "
            }}
        }}

Ví dụ 3 :
INPUT : Đổi displayname DucTM thành Tran Minh Duc(K.CNTT-HO)
OUTPUT :
{{
        "action": "add_group_member",
        "confidence": 0.85,
        "reason": "",
        "new_value": "Tran Minh Duc(K.CNTT-HO)",
        "extracted_keywords": {{
            "USER": " DucTM "
            }}
        }}

 Ví dụ 4 :
 INPUT : Đổi department HocNV sang P.VHHTDTDM
OUTPUT :
{{
        "action": "update_user_department",
        "confidence": 0.85,
        "reason": "",
        "new_value": "P.VHHTDTDM",
        "extracted_keywords": {{
            "USER": "HocNV"
            }}
        }}
   
"""

    print(
    f"[PROMPT] ACTIONS={len(actions_text)}"
    )
    print(
    f"[PROMPT] CHARS={len(prompt)}"
    )
    print(
    f"[PROMPT] KB={len(prompt)/1024:.2f}"
    )
    return prompt