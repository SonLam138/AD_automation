Bạn đang ở ROUND 2.

NHIỆM VỤ ROUND 2:
Dùng EMAIL CẦN XỬ LÝ, EMPLOYEE_EXTRACT và TOOL_RESULT để tạo JSON onboarding request cuối cùng.

ROUND 2 KHÔNG ĐƯỢC SUY LUẬN.

ROUND 2 CHỈ ĐƯỢC:
  1. Ánh xạ dữ liệu.
  2. Chuyển đổi định dạng.
  3. Ghép dữ liệu từ EMPLOYEE_EXTRACT và TOOL_RESULT.

QUY TẮC BẮT BUỘC:
- TOOL_RESULT là nguồn duy nhất để lấy target_ou, group_name, unit_code.
- Không tự bịa target_ou.
- Không tự bịa group.
- Không lấy dữ liệu từ ví dụ trong guide.
- Không giải thích, suy diễn, phân tích đối vói các kết quả đã trả ra từ TOOL
- Không viết markdown.
- Không dùng code block.
- Chỉ trả về một JSON object hợp lệ.

Nếu TOOL_RESULT.matched = false:
- target_ou = ""
- member_of = []

Nếu TOOL_RESULT.matched = true:
- Ma_chi_nhanh = TOOL_RESULT.unit_code
- target_ou = TOOL_RESULT.target_ou
- member_of = [TOOL_RESULT.group_name]

QUY TẮC TÁCH TÊN (THEO QUY ĐỊNH TÊN TIẾNG VIỆT : HỌ và ĐỆM ở trước TÊN)
- Firstname là tên cuối cùng trong "họ và tên"
- LastName là tất cả các từ còn lại trong "họ và tên"
- Bỏ dấu Tiếng việt ở tất cả các tên
- Ví dụ :
    Họ và tên : Nguyễn Minh Sơn
      + firstname : Son
      + lastname : Nguyen Minh

QUY TẮC HIỂN THỊ DISPLAYNAME :
- Bỏ dấu Tiếng Việt.
- DisplayName phải được hiển thị theo đúng format quy tắc dưới, không thay đổi vị trí, không bỏ bất cứ giá trị nào.
  <Full_name> (K.XX-YY)
- trong đó :
  + XX : là tên viết tắt bằng cách ghép tất cả các chữ cái đầu tiên trong tên Khối (lấy ở trường division_name) (Ví dụ : Khối Công nghệ thông tin --> K.CNTT)
  + YY : Ma_chi_nhanh
  + Ví dụ : Nguyen Minh Son (K.CNTT-HO)

QUY TẮC TẠO SAM_ACCOUNT_NAME:
- Bắt đầu bằng Firsname viết đầy đủ, bỏ dấu Tiếng Việt
- Sau đó lấy các chữ cái đầu tiên của phần còn lại ghép vào tạo thành Sam_account_name hoàn chỉnh
- Ví dụ : Nguyen Minh Son thì sam_account_name là Sonnm

Schema bắt buộc:

{{
  "current_task": {{
    "detected_task": "",
    "input_type": "",
    "primary_focus": "",
    "notes": ""
  }},
  "resolver_reasoning": {{
    "email_focus": "",
    "organization_match": "",
    "ou_reason": "",
    "group_reason": ""
  }},
  "resolved_data": {{
    "firstname": "",
    "lastname": "",
    "sam_account_name:: "",
    "name": "",
    "display_name": "",
    "employee_id": "",
    "title": "",
    "department_name": "",
    "target_ou": "",
    "member_of": []
  }}
}}