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

from app.auto_engine.services.review_session_container import (
    review_session_repository
)

from app.auto_engine.resolver.workflow_excel_preview import (
    create_review_session_id,
    review_offboarding_rows,
)


from app.auto_engine.resolver.workflow_excel_normalizer import normalize_columns
from app.auto_engine.resolver.workflow_excel_preview import review_offboarding_rows

import pandas as pd
from io import BytesIO
from app.auto_engine.models.employee_offboarding_adapter import (
    EmployeeOffboardingApiAdapter
)

from app.auto_engine.models.employee_offboarding import (
    EmployeeOffboardingApiRequest
)

from app.auto_engine.models.request_models import BulkConfirmRequest

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