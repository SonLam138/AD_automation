
.eml folder
  ↓
read từng email
  ↓
extract subject/from/date/body
  ↓
parse HR form deterministic
  ↓
build employee_extract
  ↓
gọi lại search_tool hiện có
  ↓
build pending_request
  ↓
append vào pending_request.json

React
  cd Onboard_UI_React
  npm run dev

Swagger (FASTAPI)  
uvicorn app.main:app --reload



Thêm Khối hoặc đổi tên Khối :
  Update lại code trong final_resolver.py
  Update file excel sử dụng cho tool
    
Sửa DisplayName phần hiển thị, vd (K.CNTT-HO):
  Update file division_code_map.json


