from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver
)

from app.auto_engine.models.employee_offboarding_adapter import (
    EmployeeOffboardingEmailAdapter,
    EmployeeOffboardingUIAdapter
)
from app.auto_engine.services.plan_generator import PlanGenerator



adapter = EmployeeOffboardingUIAdapter()

request = adapter.parse(
    {
        "employee_id": "E123456",

        "email": "son.nguyen@company.com",

        "effective_time": "09/08/2026",

        "Hình thức": "nghỉ việc",
    }
)

#
# Tạm hardcode context ở V1
#

request.context = "RESIGNED"

resolver = WorkflowResolver()

workflow = resolver.resolve(
    request
)

plan_generator = PlanGenerator()

plan = plan_generator.generate(
    request=request,
    workflow=workflow
)

#print(plan.model_dump())

print(workflow.model_dump_json(indent=2))