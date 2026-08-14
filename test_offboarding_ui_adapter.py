from app.auto_engine.models.employee_offboarding_adapter import (
    EmployeeOffboardingEmailAdapter,
    EmployeeOffboardingUIAdapter
)
from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver
)
from app.auto_engine.services.request_service import (
    RequestRepository
)

from app.auto_engine.services.request_service import (
    RequestService
)
from app.auto_engine.services.plan_generator import PlanGenerator
from app.auto_engine.services.execution_plan_repository import (
    ExecutionPlanRepository
)

from datetime import datetime

adapter = EmployeeOffboardingUIAdapter()

request = adapter.parse(
    {
        "employee_id": "001002",
        "email": "test@pvcombank.com",
        "effective_time": "10/08/2026",
        "Hình thức": "nghỉ việc"
    }
)

repo = RequestRepository()

service = RequestService(repo)

request_id = service.create_request(request)

#saved_request = service.get_request(request_id)

resolver = WorkflowResolver()

workflow = resolver.resolve(request)

plan_generator = PlanGenerator()

plan = plan_generator.generate(
    request=request,
    workflow=workflow
)
print(plan.model_dump_json(indent=2))

repo = ExecutionPlanRepository()

repo.save(plan)

print("SAVE OK")

loaded_plan = repo.get(
plan.request_id
)

print("\nLOADED PLAN")
print(loaded_plan)

from app.auto_engine.builders.active_execution_builder import (
    ActiveExecutionBuilder,
)

from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)


active_builder = ActiveExecutionBuilder()
active_repo = ActiveExecutionRepository()

active_execution = active_builder.build(
    plan
)

active_repo.save(
    active_execution
)