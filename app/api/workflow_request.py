# app/api/workflow_api.py

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File
)
from datetime import (
    datetime,
    timezone,
)

import json
from pathlib import Path

from app.auto_engine.services.review_session_container import (
    review_session_repository
)

from app.auto_engine.resolver.workflow_excel_preview import (
    create_review_session_id,
    review_offboarding_rows,
)
from app.auth.rbac import require_group
from fastapi import Depends
from app.auto_engine.resolver.workflow_registry import reload_workflow_registry

from app.auto_engine.resolver.workflow_excel_normalizer import normalize_columns
from app.auto_engine.resolver.workflow_excel_preview import review_offboarding_rows
from app.auto_engine.models.workflow_runtime_adapter import WorkflowRuntimeAdapter
import pandas as pd
from io import BytesIO
from app.auto_engine.models.employee_offboarding_adapter import (
    EmployeeOffboardingApiAdapter
)

from app.auto_engine.models.employee_offboarding import (
    EmployeeOffboardingApiRequest
)

from app.auto_engine.models.request_models import BulkConfirmRequest
from app.auto_engine.models.custom_workflow_request import CustomWorkflowSaveRequest
from app.auto_engine.models.custom_workflow_adapter import CustomWorkflowAdapter

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
from app.auto_engine.resolver.custom_workflow_validation_service import (
    CustomWorkflowValidationService
)

router = APIRouter(
    dependencies=[
        Depends(
            require_group([
                "workflow_admin"
            ])
        )
    ]
)


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


@router.post(
    "/employee-offboarding/preview"
)
async def preview_offboarding_file(
    file: UploadFile = File(...)
):

    try:

        # ==========================================
        # READ UPLOAD
        # ==========================================

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="File upload rỗng."
            )

        # ==========================================
        # READ EXCEL
        # ==========================================

        dataframe = pd.read_excel(
            BytesIO(
                contents
            )
        )

        # ==========================================
        # NORMALIZE COLUMNS
        # ==========================================

        dataframe = normalize_columns(
            dataframe
        )

        # ==========================================
        # BUILD NORMALIZED ROWS
        # ==========================================

        rows = (
            dataframe
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

        safe_rows = []

        for row in rows:

            safe_row = {}

            for key, value in row.items():

                if isinstance(
                    value,
                    pd.Timestamp
                ):

                    safe_row[key] = (
                        value.isoformat()
                    )

                else:

                    safe_row[key] = value

            safe_rows.append(
                safe_row
            )

        # ==========================================
        # RESOLVE AND REVIEW
        # ==========================================

        review_result = (
            review_offboarding_rows(
                safe_rows
            )
        )

        # ==========================================
        # CONVERT TIMESTAMPS IN REVIEW ROWS
        # ==========================================

        if review_result.get("rows"):
            for row in review_result["rows"]:
                for key, value in row.items():
                    if isinstance(value, pd.Timestamp):
                        row[key] = value.isoformat()


        created_at = (
            datetime
            .now(
                timezone.utc
            )
            .isoformat()
        )

        session_id = None

        if review_result["can_confirm"]:

            session_id = (
                create_review_session_id()
            )

            review_session = {

                "session_id":
                    session_id,

                "file_name":
                    file.filename,

                "status": "READY_FOR_CONFIRM",

                "created_at":
                    created_at,

                "request_candidates":

                    review_result[
                        "request_candidates"
                    ],

                "confirmation": {
                "confirmed_at": None,
                "created_requests": []
                }
            }

            review_session_repository.save(
                review_session
            )

        return {

            "session_id":
                session_id,

            "file_name":
                file.filename,

            "columns":
                list(
                    dataframe.columns
                ),

            **review_result
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                "Không thể review file "
                f"Offboarding: {exc}"
            )
        )

@router.post(
    "/employee-offboarding/confirm"
)
def confirm_offboarding(
    request:
        BulkConfirmRequest
):
    session = (
        review_session_repository.get(
            request.session_id
        )
    )

    for candidate in session[
        "request_candidates"
    ]:

        workflow_runtime.run_plan_engine(

            adapter=
                employee_offboarding_api_adapter,

            source_data=
                candidate
        )

    session["status"] = (
        "CONFIRMED"
    )

    review_session_repository.save(
        session
    )



@router.post("/validate")
async def validate_custom_workflow(
    payload: dict
):

    workflow_info = payload.get(
        "workflowInfo",
        {}
    )

    objects = payload.get(
        "objects",
        []
    )

    return (
        CustomWorkflowValidationService()
        .validate(
            workflow_info,
            objects
        )
    )


@router.post(
    "/custom-workflow/save"
)
def save_custom_workflow(
    request: CustomWorkflowSaveRequest
):

    adapter = (
        CustomWorkflowAdapter()
    )

    workflow_context = (
        adapter.build_workflow_context(
            request.workflowInfo,
            request.objects,
            request.steps
        )
    )

    templates = (
        adapter.build_registry_templates(
            workflow_context
        )
    )

    registry_file = (
        Path(__file__).parent.parent
        / "auto_engine"
        / "resolver"
        / "workflow_registry.json"
    )
    print(registry_file)

    with open(
        registry_file,
        "r",
        encoding="utf-8"
    ) as f:

        registry = json.load(f)

    registry.extend(
        templates
    )

    with open(
        registry_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            registry,
            f,
            indent=2,
            ensure_ascii=False
        )
    reload_workflow_registry()

    return {
        "success": True,
        "templateCount": len(templates)
    }

@router.post(
    "/custom-workflow/run"
)
def run_custom_workflow(
    request: CustomWorkflowSaveRequest
):
    adapter = (
        CustomWorkflowAdapter()
    )

    workflow_context = (
        adapter.build_workflow_context(
            request.workflowInfo,
            request.objects,
            request.steps
        )
    )
    registry_file = (
            Path(__file__).parent.parent
            / "auto_engine"
            / "resolver"
            / "workflow_registry.json"
        )
    
    with open(
        registry_file,
        "r",
        encoding="utf-8"
    ) as f:

        registry = json.load(f)

    requests = (
        adapter.build_requests(
            workflow_context,
            registry
        )
    )
  
    runtime_adapter = (
        WorkflowRuntimeAdapter()
    )

    created_plans = []

    completed_contexts = set()

    for request_item in requests:

        print("=" * 80)
        print("REQUEST CONTEXT")
        print(request_item.context)
        print("=" * 80)

        plan = (
            workflow_runtime.run_plan_engine(
                adapter=runtime_adapter,
                source_data=request_item
            )
        )

        completed_contexts.add(request_item.context)

        created_plans.append(
            plan.request_id
        )


    for template in registry:

        contexts = (
            template
            .get("match", {})
            .get("contexts", [])
        )

        if any(
            context in completed_contexts
            for context in contexts
        ):
            template[
                "workflow_complete"
            ] = True

    with open(
        registry_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            registry,
            f,
            indent=2,
            ensure_ascii=False
        )
    reload_workflow_registry()
    return {
            "success": True,
            "requestCount": len(requests),
            "planCount": len(created_plans),
            "plans": created_plans
        }

        
