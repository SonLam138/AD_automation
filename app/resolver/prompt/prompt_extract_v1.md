Bạn đang ở ROUND 1.

NHIỆM VỤ ROUND 1:
Nhiệm vụ của bạn tại round 1 là đọc email cần xử lý và tạo lookup request để tìm được OU_name và group_name

QUY TẮC BẮT BUỘC TRONG ROUND 1
  - Tạo thông tin cá nhân từ email HR
  - Tạo thông tin có giá trị lookup cho tool_search là : uinit_hint và department_hin từ những hướng dẫn thông tin tổ chức
  - Tool chỉ hiểu được 2 giá trị unit_hint và department_hint. Nếu 2 trường này sai, toàn bộ nhiệm vụ sẽ thất bại.


CÁC BƯỚC THỰC HIỆN:
- Đọc Guide hướng dẫn Round 1
- Tạo thông tin lookup như sau :
  + full_name lấy từ "Họ và tên".
  + employee_id lấy từ "Mã nhân viên", giữ nguyên số 0 đầu.
  + title lấy từ "Chức danh". 
  + division_name lấy từ Khối
  + temp_name : CHỈ lấy tên Chi nhánh từ "Phòng/ban" (bắt đầu bằng "PVcomBank"). Giữ lại tên Chi nhánh đó, bỏ các tên còn lại như phòng, bộ phận...(các tên được cách nhau bởi dấu "-"), nếu không có tên chi nhánh chuẩn PVCOMBANK thì gán temp_name = ""
- (VERY IMPORTANCE) Department_hint : CHỈ lấy tên của phòng từ "Phòng/ban" (bắt đầu bằng chữ "Phòng"). Giữ lại tên phòng, bỏ hết các tên khác như trung tâm, bộ phận..(các tên được cách nhau bởi dấu "-")
- (VERY IMPORTANCE) unit_hint : chỉ được chọn 1 trong 2 giá trị sau
  + unit_hint = division_name nếu temp_name là rỗng
  + unit_hint = temp_name nếu temp_name có giá trị

- Quy tắc bỏ dấu:
  + Chỉ bỏ dấu Tiếng Việt
  + KHÔNG xóa khoảng trắng
  + KHÔNG merge các từ lại với nhau
  + Output phải ở dạng có thể đọc hiểu theo ngôn ngữ con người
  + Ví dụ : 
    Nguyễn Minh Sơn --> Nguyen Minh Son (sai nếu là : NguyenMinhSon)
    Khối Khách hàng cá nhân --> Khoi Khach hang ca nhan (Sai nếu là Khoikhachhangcanhan)

Output mong muốn : 
  - Only json.

{{
  "current_task": {{
    "detected_task": "create_lookup_request",
    "input_type": "HR onboarding email",
    "primary_focus": ""
  }},
  "extract_reasoning": {{
    "temp_name_source_field": "",
    "unit_hint_rule_selected": "",
    "department_hint_source_field": ""
  }},
  "employee_extract": {{
    "full_name": "",
    "employee_id": "",
    "title": "",
    "division_name": "",
    "temp_name": "",
    "unit_hint": "",
    "department_hint": ""
  }}
}}

