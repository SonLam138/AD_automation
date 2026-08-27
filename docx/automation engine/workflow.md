Offboarding API:
 
 Payload :
    {
    "employee_id": "",
    "email": "ad.auto2@automate.com.vn",
    "reason": "nghỉ việc",
    "effective_time": "22/08/2026",
    "target_ou": "Disabled Account"
    }

VD curl :
    curl -X 'POST' \
    'http://localhost:8000/api/workflow/employee-offboarding' \
    -H 'accept: application/json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzb25ubSIsIm5hbWUiOiJOZ3V5ZW4gTWluaCBTb24oSy5DTlRULVRlc3QpIiwiZ3JvdXBzIjpbIndvcmtmbG93X2FkbWluIiwiYWRfc3RhdHVzX3VzZXIiLCJhZF9tb2RpZnlfdXNlciIsImFkX2NvbXB1dGVyX21nbXQiLCJhZF9tb3ZlX291IiwiYWRfZ3JvdXBfbWVtYmVyIiwiYWRfbG9naW4iLCJhZF9kaXNfdXNlciIsIk9uYm9hcmRfQXBwcm92ZV9Mb2dpbiIsIlRlc3RfZ3JwIl0sImlhdCI6MTc4NzM5NzkxNywiZXhwIjoxNzg3NDAxNTE3fQ.d8eeIqLoV6JuXfJVwpP2iSApy-ZZfNBkxjPQrx4BW38' \
    -H 'Content-Type: application/json' \
    -d '{
    "employee_id": "",
    "email": "ad.auto2@automate.com.vn",
    "reason": "nghỉ việc",
    "effective_time": "22/08/2026",
    "target_ou": "Disabled Account"
    }'


    move_user_to_ou đang dùng DN
    