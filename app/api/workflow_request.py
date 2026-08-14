# app/api/workflow_api.py

from fastapi import (
    APIRouter,
    HTTPException
)

from app.auto_engine.models.employee_offboarding_adapter import (
    EmployeeOffboardingApiAdapter
)

from app.auto_engine.models.employee_offboarding import (
    EmployeeOffboardingApiRequest
)

from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver
)

from app.auto_engine.services.plan_generator import (
    PlanGenerator
)

from app.auto_engine.services.execution_plan_repository import (
    ExecutionPlanRepository
)

from app.auto_engine.services.request_service import (
    RequestService
)

from app.auto_engine.resolver.workflow_plan_engine import (
    WorkflowPlanEngine
)

from app.auto_engine.runtime.runtime_container import workflow_runtime


router = APIRouter()


employee_offboarding_api_adapter = (
    EmployeeOffboardingApiAdapter()
)


workflow_plan_engine = WorkflowPlanEngine(
    workflow_resolver=WorkflowResolver(),

    plan_generator=PlanGenerator(),

    plan_repository=ExecutionPlanRepository()
)


@router.post(
    "/employee-offboarding"
)
def employee_offboarding(
    source_request:
        EmployeeOffboardingApiRequest,
):

    try:

        plan = (
            workflow_runtime.run_plan_engine(
                adapter=(
                    employee_offboarding_api_adapter
                ),

                source_data=(
                    source_request.model_dump()
                ),
            )
        )

        return {
            "success": True,

            "request_id":
                plan.request_id,

            "workflow_id":
                plan.workflow_id,

            "execute_at":
                plan.execute_at,
        }

    except ValueError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex),
        )

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )