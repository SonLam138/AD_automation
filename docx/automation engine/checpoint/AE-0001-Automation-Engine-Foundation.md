# AE-0001: Automation Engine Foundation

- **Status:** Accepted
- **Decision Type:** Architecture Foundation
- **Scope:** AD Automation Framework / Automation Engine
- **Created:** 2026-08-06
- **Supersedes:** None
- **Superseded by:** None

---

## 1. Context

Yêu cầu ban đầu là tự động thu hồi tài khoản AD của nhân sự nghỉ việc.

Trong quá trình phân tích, yêu cầu này mở rộng thành nhiều trường hợp AD Automation khác:

- Thu hồi tài khoản nghỉ việc đúng ngày hiệu lực.
- Onboarding theo thông tin từ HR hoặc ServiceDesk.
- Thực hiện action hàng loạt từ dữ liệu rà soát.
- Cấp quyền tạm thời rồi tự động thu hồi.
- Đối chiếu trạng thái object giữa AD và hệ thống khác.
- Xử lý kết quả lookup như inactive user hoặc inactive computer.
- Cho phép cán bộ IT đặc quyền tự ghép nhiều AD action theo thời gian.
- Tiếp nhận cùng một yêu cầu nghiệp vụ từ nhiều nguồn khác nhau như UI, API, email, file hoặc hệ thống tích hợp.

Nếu xây riêng một module Offboarding hoặc chỉ xây Scheduled Action Engine, framework sẽ bị giới hạn theo use case đầu tiên và khó mở rộng sang các yêu cầu tiếp theo.

Automation Engine vì vậy được xác định là một trong các thành phần điều hành cốt lõi của AD Automation Framework.

---

## 2. Primary Decision

Automation Engine được thiết kế theo chuỗi khái niệm nền tảng:

```text
External Input (UI/API/Email/Excel)
2
↓
3
Source Adapter
4
↓
5
Normalized Request
6
↓
7
Workflow Resolver
8
↓
9
Workflow Definition
10
↓
11
Plan Generator
12
↓
13
ExecutionPlan
14
↓
15
ExecutionPlanRepository

Decision 01: Request Type Is the Primary Domain Entry
Decision 02: Source Is an Extension Point, Not the Business Domain
Decision 03: Generic Core Belongs to the Orchestration Layer
Decision 05: Object First Is a Mandatory Design Principle