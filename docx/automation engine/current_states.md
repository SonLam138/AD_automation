## 1. Current Objective Design an Automation Engine as a core orchestration capability of the AD Automation Framework. The initial business demand is automated offboarding, but the architecture must also support: - Onboarding. - Scheduled object actions. - Temporary access assignment and automatic revocation. - Batch or bulk object processing. - AD reconciliation with HR or other systems. - Review flows generated from lookup results. - Controlled custom workflows for privileged IT users. - Multiple input sources without coupling the domain to a source. The engine is limited to the AD domain and the existing or future AD Tool/Action Catalog. It is not intended to become a general workflow or connector platform. --- ## 2. Current Architecture ```text External Input ↓ Input Adapter ↓ Normalized Request ↓ Request Type Classification ↓ Workflow Selection or Workflow Definition ↓ Workflow Instance ↓ Workflow Steps ↓ Jobs and Schedules ↓ Generic Orchestration Core ↓ AD Action Executor ↓ Target Object



# Current State : 09/08/2026

## Đã hoàn thành

### Request Layer

✅ Request model

✅ Request ID

✅ RequestRepository (RAM)

✅ RequestService

### Source Layer

✅ UI Adapter

✅ Email Adapter

### Workflow Layer

✅ Workflow Registry

✅ WorkflowDefinition

✅ WorkflowResolver

✅ Context Matching

### Planning Layer

✅ ExecutionPlan

✅ PlanGenerator

✅ Metadata Driven Trigger Resolution

## Kiến trúc hiện tại

Request
↓
RequestService
↓
WorkflowResolver
↓
WorkflowDefinition
↓
ExecutionPlan

## Nguyên tắc đã chốt

### Request là domain trung tâm

Request Type là trung tâm phân loại nghiệp vụ.

Source chỉ là extension point.

### Workflow Resolver là trung tâm điều phối

Resolver quyết định:

- workflow nào được dùng
- template nào được dùng

Resolver không thực hiện nghiệp vụ.

### Tri thức nằm trong Registry

Registry chứa:

- workflow_id
- metadata
- actions
- dependencies

Runtime không được hardcode nghiệp vụ.

### ExecutionPlan là điểm kết thúc của Knowledge Layer

ExecutionPlan là snapshot đã được resolve đầy đủ để bước sang Runtime Layer.

ExecutionPlan chứa:

- request_id
- workflow_id
- execute_at
- actions

### RequestRepository chỉ phục vụ Request Layer

Runtime tương lai không được phụ thuộc vào:

request_service.get_request()

sau khi ExecutionPlan đã được sinh ra.

## Câu hỏi mở cho phiên tiếp theo

### Runtime Layer

Cần thống nhất:

ExecutionPlan
↓
?
↓
Action Executor

Hiện chưa chốt:

- Scheduler chịu trách nhiệm đến đâu
- Có cần tách Execution Engine hay không
- Cách xử lý depends_on
- Cách xử lý delay_minutes
- Cách xử lý retry_count
- Persistence của Runtime

Định hướng hiện tại:

Không over-engineering.

Ưu tiên Happy Case trước:

ExecutionPlan
→ Scheduler
→ Action Executor

Sau khi chạy được E2E mới mở rộng thêm retry, event và persistence.

Ngày 10/08/2026
ExecutionPlanRepository = Trusted Archive

ActiveExecutionRepository = Runtime Working Set

RuntimeScheduler = giải quyết execute_at

PlanRunner = giải quyết depends_on

ExecutionState/RuntimeManager đã rollback và xóa hoàn toàn

Business Phase hoàn thành

Runtime Phase mới hoàn thành:
- Scheduler
- PlanRunner

Chưa có RuntimeEngine để nối thành flow E2E

11/08/2026
Đã tạo được engine để thực hiện toàn bộ quá trình tạo PlaneExcution từ Input, đã viết code với APIAdapter đầu tiên, còn thiếu emaildapter và UIadapter
Luồng chính thức :
    External Input
    → Request-Type-Specific Source Adapter
    → Normalized Request
    → WorkflowPlanEngine
    → WorkflowResolver
    → WorkflowDefinition
    → PlanGenerator
    → Persisted ExecutionPlan

12/08
API
 ↓
EmployeeOffboardingApiAdapter

 ↓

WorkflowPlanEngine

 ↓

ExecutionPlan.json

 ↓

plan_to_active()

 ↓

ActiveExecution.json

 ↓

WorkflowRuntime

 ↓

WorkflowEngine.tick()

 ↓

Scheduler.scan()

 ↓

Job.json    ✅

15-08-2026 : E2E API Request theo luồng :
Source
 ↓
Adapter
 ↓
Object Resolution
 ↓
Request
 ↓
WorkflowPlanEngine
 ↓
ExecutionPlan
 ↓
ActiveExecution
 ↓
Scheduler
 ↓
Job
 ↓
Worker
 ↓
Action Registry
 ↓
Capability Action
 ↓
Target System