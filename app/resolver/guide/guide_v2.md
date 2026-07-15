=================================================================
I. ROUND 1 : Quy trình, quy định về việc tạo thông tin lookup
=================================================================
1. Mục tiêu Round 1 là : tạo thông tin lookup dùng cho round 2 từ nội dung email cần xử lý
2. Quy trình tạo thông tin lookup :
    Đọc hiểu thông tin thực tế từ email của HR
        Họ và tên
        Mã nhân viên
        Ngày Sinh
        Chức danh
        Phòng/Ban 
        Khối
    Đọc guide để nắm cơ cấu tổ chức trước khi thực hiện tạo thông tin lookup
        Khối : là đơn vị lớn nhất
        Trung tâm : là đơn vị thuộc Khối
        Chi nhánh : là đơn vị thuộc Khối, luôn bắt đầu bằng PVCOMBANK
        Phòng/bộ phận : có 2 loại : phòng thuộc Chi nhánh và phòng thuộc Khối (còn được gọi là phòng Hội sở). Phòng thuộc Khối sẽ không thuộc Chi nhánh 
    Quy tắc tạo lookup :
        Với các trường thuộc loại thông tin cá nhân, sử dụng trực tiếp thông tin từ HR
        Với các trường thông tin tổ chức, phân biệt rõ Khối, Trung tâm, Chi nhánh, Phòng/bộ phận
        Trường output mục tiêu để thực hiện lookup là :
            temp_name : trường trung gian để gán cho unit_hint.
                temp_name = "" thì gán unit_hint = tên Khối (bỏ dấu Tiếng Việt)
                temp_name có giá trị thì gán unit_hint = temp_name
            unit_hint : là trường thể hiện tên Khối hoặc Chi nhánh sử dụng cho lookup (không sử dụng trung tâm )
            department_hint : là trường thể hiện phòng sử dụng cho lookup
3. Quy định CẤM :
    Không tự ý tạo thông tin Khối, Chi nhánh, phòng/bộ phận
    Chỉ được sử dụng dữ liệu extract từ email

4. Hướng dẫn bỏ dấu tiếng việt :
    â, ă --> a
    ê --> e
    ư ---> u
    ô, ơ --> o


========================================================================
II. ROUND 2 : quy trình, quy định khi thực hiện resolve
=========================================================================
1. Mục tiêu :
    - Từ Employee Information, chuyển đổi thành onboarding request dạng AD Attribute
2. Quy trình bắt buộc :
    - Dựa vào thông tin extract từ Round 1 + kết quả của Result_tool thực hiện chuyển đổi
    - Đọc GUIDE resolve để nắm quy trình, quy định chuyển đổi các thuộc tính
    (VERY IMPORTANCE) Các thông tin bắt buộc phải resolve :
     + firstName
     + lastName
     + sAMAccountName
     + DisplayName
     + OUName
     + Groups

3. Các quy định CẤM:
    - KHÔNG được tự ý tạo group, OUname và các thông tin khác

4. Các quy định chuyển đổi thuộc tính cụ thể :

   * QUY TẮC TÁCH TÊN (THEO QUY ĐỊNH TÊN TIẾNG VIỆT : HỌ và ĐỆM ở trước TÊN)
    - Firstname là tên cuối cùng trong "họ và tên"
    - LastName là tất cả các từ còn lại trong "họ và tên"
    - Bỏ dấu Tiếng việt ở tất cả các tên
    - Ví dụ :
        Họ và tên : Nguyễn Minh Sơn
        + firstname : Son
        + lastname : Nguyen Minh

   * QUY TẮC HIỂN THỊ DISPLAYNAME :
    - Bỏ dấu Tiếng Việt.
    - DisplayName phải được hiển thị theo đúng format quy tắc dưới, không thay đổi vị trí, không bỏ bất cứ giá trị nào.
    <Full_name> (K.XX-YY)
    - trong đó :
    + XX : là tên viết tắt bằng cách ghép tất cả các chữ cái đầu tiên trong tên Khối (lấy ở trường division_name) (Ví dụ : Khối Công nghệ thông tin --> K.CNTT)
    + YY : Ma_chi_nhanh
    + Ví dụ : Nguyen Minh Son (K.CNTT-HO)

   * QUY TẮC TẠO SAM_ACCOUNT_NAME:
    - Bắt đầu bằng Firsname viết đầy đủ, bỏ dấu Tiếng Việt
    - Sau đó lấy các chữ cái đầu tiên của phần còn lại ghép vào tạo thành Sam_account_name hoàn chỉnh
    - Ví dụ : Nguyen Minh Son thì sam_account_name là Sonnm
