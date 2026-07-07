AD AUTOMATION TECHNICAL PLAYBOOK
Chương 1 - Kiến trúc tổng thể
        React UI
            ↓
        FastAPI API Layer
            ↓
        Business Service Layer
            ↓
        LDAP Adapter
            ↓
        Active Directory

1. Vai trò từng khối
React
        Hiển thị
        Thu dữ liệu
        Gọi API
    không xử lý :
        Authentication
        Authorization
        AD
FastAPI
    chỉ :
        Expose API

        /login
        /pending
        /new
Service Layer : nơi chứa các nghiệp vụ
    authenticate_user()

    create_user()

    add_group()

LDAP Adapter : nơi duy nhất làm việc trực tiếp với AD.

Chương 2 - Runtime Authentication
Luồng Login
            React Login
                    ↓
            POST /onboard_auth/login
                    ↓
            authenticate_user()
                    ↓
            authenticate_and_get_profile()
                    ↓
            AD Bind
                    ↓
            memberOf
                    ↓
            create_access_token()
                    ↓
            JWT
                    ↓
            React localStorage
a. authenticate_and_get_profile()
    Service Bind
        Connection(
            service_account
        )
    Search user
        (sAMAccountName=username)
        lấy info :
            displayName
            mail
            memberOf
            distinguishedName
    User Bind : xác thực user thật
        Connection(
            user_dn,
            password
        )
    Build User Context
        {
            username,
            display_name,
            groups
        }

Chương 3 - JWT
    Hàm sinh JWT : auth_service.create_access_token()
    payload = data.copy() tức là :
        {
            username,
            display_name,
            groups,
            exp
        }
    JWT được dùng ở đâu : Khi API có 
        Depends(
            get_current_user
        )
    get_current_user() : 
        current_user
        Payload --> jwt.decode

Chương 4 - Authorization
Nguồn thật sự và duy nhất : AD group
Mapping AD Group - các permission trong hệ

Chương 5 - API Permission
        User
            ↓
        JWT
            ↓
        get_current_user()
            ↓
        require_group()
            ↓
        API
    dùng : require_group() : kiểm tra AD group --> phân quyền tương ứng (trong mapping group)
        Depends(
            require_group(
                ["Onboard_Execute"] (quyền chạy API new_onboarding)
            )
        )

Chương 6 - Create User Runtime
        User Login
            ↓
        AD Authenticate
            ↓
        JWT
            ↓
        Approve Button
            ↓
        POST /onboarding/new
            ↓
        require_group()
            ↓
        ldap.create_user()
            ↓
        Service Account
            ↓
        AD

Chương 7 - Nguyên tắc mở rộng
Khi thêm capability mới: disable user, add/remove group
Luôn làm theo các bước :
Bước 1 :
    Định nghĩa AD group --> permission (ResetPassword_Execute)
Bước 2 :
    Tạo API ( vd post group/add or group/remove)
Bước 3 : Authorization
    require_group(
        ["ResetPassword_Execute"]
    )
Bước 4 : LDAP Adapter (thực hiện action thật lên AD)
        reset_password()
Bước 5 : Audit


