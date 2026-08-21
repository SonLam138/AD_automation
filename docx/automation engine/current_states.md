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



17/08 : sau khi hoàn thành UI của custom workflow

Một Source mới
+
Một CustomAdapter mới

Luồng bắt buộc:
UI Source
    ↓
CustomAdapter
    ↓
Request chuẩn + Registry Template
    ↓
WorkflowResolver
    ↓
WorkflowDefinition
    ↓
WorkflowPlanEngine
    ↓
PlanGenerator
    ↓
ExecutionPlanRepository
    ↓
ActiveExecution
    ↓
Scheduler
    ↓
Worker


Các lớp phía sau Resolver phải được reuse nguyên trạng. Không sửa:
    WorkflowPlanEngine
    PlanGenerator
    ExecutionPlanRepository
    ActiveExecution
    Scheduler
    Worker
    Job runtime

2. Dependency cốt lõi đã được nhận diện
với Custom Workflow: Registry chưa tồn tại
trong khi Resolver lại hoạt động như sau:
        key = (
            request.request_type,
            request.context
        )

        for workflow_data in WORKFLOW_REGISTRY:
            ...
Vì vậy, trước khi gọi Resolver, CustomAdapter bắt buộc phải hoàn thành ba sản phẩm đồng thời: 
    Request chuẩn
    Custom Registry Template
    Business_data

                UI Source
                ↓
            CustomAdapter parse dữ liệu
                ↓
            Build Request
                +
            Build Registry Template
                ↓
            Register template thành công
                ↓
            Build business_data dựa trên các object_resolver()
                ↓
            WorkflowResolver.resolve(request)
                ↓
            WorkflowDefinition

Source Model của Step đã chốt
Mỗi step hiện có :
    {
    id: Date.now(),

    objectRef: "",

    action: "",

    executeTime: "",

    dependsOn: "",

    delayMinutes: 0,

    parameters: {},

    parameterStatus: "EDITING"
}
Ý nghĩa :
    objectRef
    → Alias của object từ Object Catalog

    action
    → Business action do admin chọn

    executeTime
    → Thời điểm cụ thể do admin nhập

    dependsOn
    → Step dependency

    delayMinutes
    → Khoảng trễ sau dependency

    parameters
    → Business data riêng của action

    parameterStatus
    → EDITING hoặc CONFIRMED

UI không sinh action_code trực tiếp

Action Parameters : bổ sung dữ liệu với các action CREATE, MOVE OU
Nguyên tắc mapping :
Tên field trong UI parameters
=
Tên field schema backend cần

Final Validation tập trung
Năm tầng validation V1
    Tầng 1: Workflow
        Workflow Name bắt buộc
        Có ít nhất một Object
        Có ít nhất một Step
    Tầng 2: Step
        Mỗi Step phải có Object
        Mỗi Step phải có Action
    Tầng 3: Parameters
        parameterStatus phải là CONFIRMED
    Tầng 4: Dependency
        dependsOn phải tham chiếu đến step còn tồn tại
    Tầng 5: Time
        Step 1 → Step 2 → Step 3
    
Multi-object policy bắt buộc phải nhớ : create nhiều single request
            Many source candidates
            ↓
        Normalize
            ↓
        For each candidate / single unit
            ↓
        Reuse luồng Single hiện hữu

Mục tiêu Registry Template ở giai đoạn tiếp theo
CustomAdapter phải compile UI Source Model thành một registry entry hợp lệ kiểu:
        {
        "match": {
            "request_type":
                RequestType.CUSTOM_WORKFLOW,

            "contexts": [
                "<UNIQUE_CONTEXT_FROM_UI>"
            ]
        },

        "workflow_id":
            "<WORKFLOW_ID_FROM_UI>",

        "workflow_name":
            "<WORKFLOW_NAME_FROM_UI>",

        "object_resolver":
            "<RESOLVER_RULE>",

        "metadata": {
            "target_object_type": "MIXED",
            "schedule_mode": "CUSTOM",
            "priority": "NORMAL",
            "allow_retry": True,
            "max_retry": 3
        },

        "actions": [
            {
                "id": "STEP_01",

                "action_code":
                    "<COMPILED_FROM_OBJECT_TYPE_AND_ACTION>",

                "display_name":
                    "<DERIVED_FROM_ACTION_CATALOG>",

                "execution": {
                    "depends_on": [],
                    "delay_minutes": 0,
                    "retry_count": 3,
                    "continue_on_error": False
                }
            }
        ]
    }


WorkflowDefinition vẫn thuộc về Resolver : CustomAdapter không trả WorkflowDefinition trực tiếp. Adapter tạo và đăng ký registry template

Câu nói hôm nay :

UI vừa hoàn thành không phải một form tạo workflow để trưng bày. Nó là Source Authoring Layer, tạo đủ dữ liệu để CustomAdapter build Request, business_data và custom registry template trước khi gọi WorkflowResolver.

Và:

Resolver vẫn là nơi duy nhất sinh WorkflowDefinition. Runtime phía sau tuyệt đối không biết workflow đến từ template hard-code hay UI custom.