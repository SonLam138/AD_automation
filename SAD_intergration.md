# AD Automation Integration Security Architecture
Version: 2026-10
Status: Approved

---

# 1. Mục tiêu

Thiết kế Integration Framework nhằm cho phép các hệ thống bên ngoài gọi tới AD Automation một cách an toàn, có kiểm soát và có khả năng mở rộng trong tương lai.

Các ví dụ Integration Client:

- Mail Platform
- Portal
- Future Workflow Engine
- HR Integration
- Asset Management System
- Third-party Automation

Framework phải đảm bảo:

- Tách Authentication và Authorization.
- Không hard-code client trong từng API.
- Có thể thêm client mới mà không sửa logic endpoint.
- Có thể thu hồi quyền ngay lập tức.
- Có thể mở rộng thêm capability mới trong tương lai.

---

# 2. Các loại Token

## User Access Token

Đối tượng:

- Người dùng đăng nhập Portal

Mục đích:

- Xác thực user
- Phân quyền theo AD Group

Ví dụ:

```text
Portal User
    →
User Access Token
    →
AD Automation
```

---

## Service Token

Đối tượng:

- Trusted Internal Service

Ví dụ:

- Mail Platform Offboarding
- Internal Scheduler
- Internal Workflow Runtime

Mục đích:

- Service-to-Service Communication

Ví dụ:

```text
Mail Platform
    →
Service Token
    →
/employee-offboarding
```

---

## Integration Token

Đối tượng:

- Registered Integration Client

Ví dụ:

- Mail Platform
- Portal
- Future Applications

Mục đích:

- Xác thực Integration Client

Ví dụ:

```text
Mail Platform
    →
client_id + client_secret
    →
Integration Token
    →
Integration API
```

---

# 3. Phân tách Authentication và Authorization

Đây là nguyên tắc kiến trúc quan trọng nhất.

```text
Authentication
    xác định:
        "Ai đang gọi"

Authorization
    xác định:
        "Được phép làm gì"
```

Không được trộn hai khái niệm này với nhau.

---

# 4. Authentication Flow

## Bước 1

Client gọi:

```http
POST /api/v1/service/integration/token
```

Body:

```json
{
    "client_id": "mail-platform",
    "client_secret": "xxxxx"
}
```

---

## Bước 2

AD Automation kiểm tra:

```python
INTEGRATION_CLIENTS
```

Điều kiện:

```text
Client tồn tại
Client enabled
Client Secret hợp lệ
```

---

## Bước 3

Sinh JWT

Ví dụ claim:

```json
{
    "iss": "ad-automation",
    "sub": "mail-platform",
    "aud": "ad-automation",
    "actor_type": "integration"
}
```

---

## Bước 4

Client nhận token:

```json
{
    "access_token": "...",
    "token_type": "bearer"
}
```

---

## Bước 5

Client gọi API:

```http
Authorization: Bearer <token>
```

---

# 5. Authorization Flow

Sau khi token hợp lệ:

```python
verify_integration_token()
```

hệ thống thực hiện phân quyền.

---

## Luồng xử lý

```text
Token
    ↓
verify_integration_token
    ↓
claims["sub"]
    ↓
client_id
    ↓
INTEGRATION_CLIENTS
    ↓
allowed_endpoints
    ↓
Authorize
```

---

# 6. Integration Registry

Ví dụ:

```python
INTEGRATION_CLIENTS = {

    "mail-platform": {

        "display_name":
            "Mail Platform",

        "client_secret":
            "mail-platform-secret-2026",

        "allowed_endpoints": [

            "create_object",

            "disable_object",

            "enable_object",

            "basic_attribute",

            "group_member_add",

            "group_member_remove",

            "move_to_ou",
        ],

        "enabled": True,
    }
}
```

---

# 7. Capability Model

Framework sử dụng Capability Authorization.

Không phân quyền theo URL.

Không phân quyền theo Request.

Không phân quyền theo Object.

Phân quyền theo năng lực.

---

## create_object

Cho phép:

```text
Create User
Create Group
```

Endpoint:

```text
/integration/ad/users/create

/integration/ad/groups/create
```

---

## disable_object

Cho phép:

```text
Disable User
Disable Computer
```

Endpoint:

```text
/integration/ad/users/disable

/integration/ad/computers/disable
```

---

## enable_object

Cho phép:

```text
Enable User
Enable Computer
```

Endpoint:

```text
/integration/ad/users/enable

/integration/ad/computers/enable
```

---

## basic_attribute

Cho phép:

```text
Update Display Name
Update Department
Update IP Phone
Update Description
```

Endpoint:

```text
/integration/ad/users/update-display-name

/integration/ad/users/update-department

/integration/ad/users/update-ip-phone

/integration/ad/users/update-description
```

---

## group_member_add

Cho phép:

```text
Add User/Group/Computer
into Group
```

Endpoint:

```text
/ integration/ad/group-members/add
```

---

## group_member_remove

Cho phép:

```text
Remove User/Group/Computer
from Group
```

Endpoint:

```text
/ integration/ad/group-members/remove
```

---

## move_to_ou

Cho phép:

```text
Move User
Move Computer
Move Group
```

Endpoint:

```text
/ integration/ad/move-to-ou
```

---

# 8. Dependency Authorization

Tất cả Integration Endpoint phải sử dụng:

```python
require_integration_endpoint(
    endpoint_key
)
```

Ví dụ:

```python
@router.post(
    "/integration/ad/group-members/add"
)
def integration_ad_add_user_to_group(

    request:
        IntegrationGroupMemberRequest,

    claims=Depends(
        require_integration_endpoint(
            "group_member_add"
        )
    ),
):
```

---

Dependency sẽ:

```text
1. Verify JWT

2. Lấy client_id từ claim.sub

3. Tìm client trong registry

4. Kiểm tra enabled

5. Kiểm tra allowed_endpoints

6. Trả 403 nếu không được phép
```

---

# 9. Tại sao không đưa allowed_endpoints vào JWT

Không nhúng permission vào token.

Permission chỉ nằm trong Registry.

Lý do:

Nếu quyền thay đổi:

```python
allowed_endpoints=[]
```

thì tác động ngay lập tức.

Không phải chờ:

```text
JWT hết hạn
```

mới có hiệu lực.

---

# 10. Phạm vi của Authorization hiện tại

Authorization hiện tại trả lời câu hỏi:

```text
Client này có được phép sử dụng Capability này hay không?
```

Ví dụ:

```text
Mail Platform
    →
Capability:
        group_member_add
```

↓

Cho phép gọi:

```text
/integration/ad/group-members/add
```

↓

PASS

---

Ví dụ:

```text
Mail Platform
    →
Capability:
        disable_object
```

↓

Cho phép gọi:

```text
/integration/ad/users/disable

/integration/ad/computers/disable
```

↓

PASS

---

Ví dụ:

```text
Portal
```

không được cấp:

```text
disable_object
```

nhưng cố gắng gọi:

```text
/integration/ad/users/disable
```

↓

```http
403 Forbidden
```

---

## Phân quyền hiện tại KHÔNG kiểm tra

Authorization hiện tại không trả lời:

```text
User nào được disable

Group nào được add member

OU nào được move

Request có hợp lệ hay không

Business rule có đúng hay không
```

Các kiểm tra này thuộc lớp khác:

```text
Business Validation

Workflow Validation

LDAP Validation
```

---

## Capability-Based Authorization

Authorization hiện tại được thiết kế theo Capability.

Không phân quyền theo:

```text
Request

Mail

Action Code

LDAP Object
```

Mà phân quyền theo:

```text
Năng lực của Client
```

Ví dụ:

```python
"mail-platform": {

    "allowed_endpoints": [

        "create_object",

        "disable_object",

        "enable_object",

        "basic_attribute",

        "group_member_add",

        "group_member_remove",

        "move_to_ou",
    ]
}
```

Khi được cấp:

```text
disable_object
```

Mail Platform được sử dụng toàn bộ năng lực:

```text
Disable User

Disable Computer
```

---

## Ý nghĩa thực tế

Authorization hiện tại không nhằm giới hạn:

```text
Mail nào được Disable User

Mail nào được Enable User

Mail nào được Add Group
```

Việc phân biệt các Request này thuộc trách nhiệm của:

```text
Mail Platform
```

AD Automation chỉ xác định:

```text
Client Mail Platform
    có được phép sử dụng
    Disable Capability hay không
```

---

## Các năng lực hiện đang được định nghĩa

```text
create_object

disable_object

enable_object

basic_attribute

group_member_add

group_member_remove

move_to_ou
```

---

## Ví dụ mở rộng trong tương lai

Nếu xuất hiện Endpoint mới:

```text
Reset Password
```

Có thể định nghĩa Capability mới:

```text
reset_password
```

Sau đó:

```python
require_integration_endpoint(
    "reset_password"
)
```

và cấp quyền cho từng Client thông qua Registry.

Không cần sửa:

```text
JWT

Authentication Flow

Token Generation

Token Verification