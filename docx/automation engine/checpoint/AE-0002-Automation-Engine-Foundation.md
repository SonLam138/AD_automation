
# AE-0001: Automation Engine Foundation : Workflow Resolver & Execution Plan hoàn chỉnh

## Mục tiêu

Hoàn thiện tầng Knowledge Layer của AD Automation Engine.

Luồng xử lý hiện tại:

Request
→ RequestService
→ WorkflowResolver
→ WorkflowDefinition
→ ExecutionPlan

## Các thay đổi chính

### 1. Request ID

Request đã được bổ sung request_id và được cấp ID tại RequestService.

Format hiện tại:

REQ_DDMMYYYY_XXXX

Ví dụ:

REQ_09082026_F3A1

Lưu ý:

- Request ID là correlation ID xuyên suốt toàn bộ hệ thống.
- Request ID được mang theo từ Request tới ExecutionPlan.
- Runtime không được phụ thuộc vào việc lookup RequestRepository để lấy lại Request.

### 2. WorkflowDefinition

Chuẩn hóa dùng duy nhất:

workflow_id

Loại bỏ hoàn toàn workflow_code để tránh tồn tại hai định danh khác nhau cho cùng một workflow.

Ví dụ:

OFFBOARDING_RESIGNED

### 3. Workflow Metadata

Thông tin runtime được giữ trong metadata của workflow.

Ví dụ:

{
    "target_object_type": "USER",
    "schedule_mode": "AT_EFFECTIVE_TIME",
    "trigger_field": "effective_time"
}

PlanGenerator đọc trigger_field từ metadata.

Không hardcode scheduling logic trong runtime.

### 4. ExecutionPlan

Tạo model ExecutionPlan.

Schema hiện tại:

- request_id
- workflow_id
- execute_at
- actions

Actions được lấy nguyên từ Workflow Registry.

Không generate lại.
Không sửa dependency.
Không thay đổi delay/retry.

### 5. PlanGenerator

PlanGenerator có nhiệm vụ:

- nhận Request
- nhận WorkflowDefinition
- lấy trigger_field từ metadata
- resolve execute_at từ payload
- sinh ExecutionPlan

PlanGenerator không chứa nghiệp vụ.

Toàn bộ tri thức vẫn nằm trong Registry.

## Trạng thái hiện tại

Đã test thành công end-to-end:

Request
→ WorkflowResolver
→ ExecutionPlan

Ví dụ output:

{
  "request_id": "REQ_09082026_F3A1",
  "workflow_id": "OFFBOARDING_RESIGNED",
  "execute_at": "2026-08-09T00:00:00",
  "actions": [...]
}

## Chưa triển khai

- Scheduler
- Action Execution Runtime
- Retry Runtime
- Event System
- Persistence Runtime