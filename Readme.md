Onboarding
Offboarding
Reset Password
Unlock User
Add Group

1. Triết lý thiết kế :
    Deterministic First 
    AD là nguồn sự thật.
    AI không quyết định hành động.
    AI chỉ hỗ trợ hiển thị, giải thích,tóm tắt hoặc xác nhận.

2. Kiến trúc tổng thể
    Layer 1 - UI
        React
        Chức năng : 
            Login
            Pending Requests (list row)
            Review
            Approve

    Layer 2 - API
        FastAPI
            / onboard_auth/login
            / onboarding/requests/pending
            / onboarding/new

    Layer 3 - Business Service
        authenticate_user()
    
        create_user()
    
        add_group()

    Layer 4 - Active Directory
        LDAP / LDAPS
        Users
        Groups
        OU

3. Nguyên tắc Authentication
    AD User
    LDAPS Bind
    memberOf
    Runtime :
        React Login
            ↓
        /onboard_auth/login
            ↓
        authenticate_user()
            ↓
        LDAPS
            ↓
        memberOf
            ↓
        JWT

4. Nguyên tắc Authorization : lấy group AD làm trục chính
    Login Permission
    Execute Permission
    Read Permission

5. JWT Design
    chỉ dùng cho Identity Context (ngữ cảnh khi đã login hay còn gọi user context)
    payload :  
        {
            "username": "...",
            "display_name": "...",
            "groups": [...]
        }

6. API Permission Model
    Login (ADgroup : Onboard_Approve_Login)
--> API Permission (ADgroup : Onboard_Read, Onboard_Execute...)
--> Execute Confirmation (API aprrove, munal action approve...)
