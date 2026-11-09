# app/api/workflow_api.py

import os
import tempfile
import json
import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File
)
from typing import Any, Dict
from datetime import (
    datetime,
    timezone,
)

from app.ra_soat.account_discovery import discover_users_and_build_requests
from app.ra_soat.file_loader import *
from app.adapters.ldap_container import (
    ldap,
)
from app.search_tools.ou_search import search_ou
from app.search_tools.group_search import search_group
from pathlib import Path

from app.auto_engine.services.review_session_container import (
    review_session_repository
)
from app.auto_engine.services.workflow_journal_repository import (
    WorkflowJournalRepository,
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
from app.auto_engine.models.wf_with_newvalue_adapter import TargetObjectWithNewValueAdapter
from app.auto_engine.models.wf_with_newvalue import TempResolveObjectRequest
from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver
)

from app.auto_engine.services.plan_generator import (
    PlanGenerator
)

# from app.auto_engine.services.execution_plan_repository import (
#     ExecutionPlanRepository
# )

# from app.auto_engine.services.request_service import (
#     RequestService
# )

from app.auto_engine.resolver.workflow_plan_engine import (
    WorkflowPlanEngine
)

from app.auto_engine.runtime.runtime_container import workflow_runtime
from app.auto_engine.resolver.custom_workflow_validation_service import (
    CustomWorkflowValidationService
)
from app.auto_engine.sqlite.sql_execution_plan_repository import (SqlExecutionPlanRepository,)
from app.auto_engine.sqlite.mail_request_audit_repository import MailRequestAuditRepository
from app.auto_engine.sqlite.mail_request_audit_record import MailRequestAuditRecord
from app.auto_engine.sqlite.offboarding_audit_repository import (
    OffboardingAuditRepository,
)
from app.auto_engine.sqlite.access_snapshot_repository import AccessSnapshotRepository
from app.auto_engine.services.access_snapshot_service import AccessSnapshotService
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
mail_request_audit_repository = (
    MailRequestAuditRepository()
)
offboarding_audit_repository = (
    OffboardingAuditRepository()
)

wf_with_newvalue_adapter = (TargetObjectWithNewValueAdapter())


access_snapshot_repository = (
AccessSnapshotRepository()
)

access_snapshot_service = (
    AccessSnapshotService(
    AccessSnapshotRepository()
    )
    )

workflow_plan_engine = WorkflowPlanEngine(
    workflow_resolver=WorkflowResolver(),

    plan_generator=PlanGenerator(),

    plan_repository=SqlExecutionPlanRepository()
)


def _save_mail_offboarding_audit(
    source_request: EmployeeOffboardingApiRequest,
    response: dict,
) -> None:
    if str(source_request.source_type or "").lower() != "email":
        return

    request_id = response.get("request_id")
    workflow_id = response.get("workflow_id")
    if not request_id or not workflow_id:
        raise RuntimeError(
            "Offboarding response is missing request_id or workflow_id"
        )

    if mail_request_audit_repository.get_by_request_id(request_id):
        return

    mail_request_audit_repository.save(
        MailRequestAuditRecord(
            request_id=request_id,
            workflow_id=workflow_id,
            request_type="EMPLOYEE_OFFBOARDING",
            reason=source_request.reason,
            employee_id=source_request.employee_id,
            email=str(source_request.email),
            source_reference=source_request.source_reference,
            sender=source_request.sender,
            subject=source_request.subject,
            is_emergency=source_request.is_emergency,
            created_at=datetime.now(),
        )
    )


def create_offboarding_plan(
    source_request:
        EmployeeOffboardingApiRequest
):
    source_data = source_request.model_dump(
        mode="python"
    )
    source_request_id = (
        source_data.get("source_request_id")
        or source_data.get("source_reference")
        or f"OFFBOARDING-{uuid.uuid4()}"
    )
    source_request.source_request_id = str(
        source_request_id
    )
    source_data["source_request_id"] = (
        source_request.source_request_id
    )

    parsed_request = employee_offboarding_api_adapter.parse(
        source_data
    )
    business_data = parsed_request.business_data
    requested_account = business_data[
        "target_object"
    ]["sam_account_name"]
    record, claimed = offboarding_audit_repository.claim(
        source_request_id=source_request.source_request_id,
        employee_id=source_request.employee_id.strip(),
        requested_account=requested_account.strip(),
    )

    if not claimed:
        same_employee = (
            record.employee_id.strip()
            == source_request.employee_id.strip()
        )
        same_account = (
            record.requested_account.strip().casefold()
            == requested_account.strip().casefold()
        )
        if not same_employee or not same_account:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "idempotency_key_payload_mismatch",
                    "message": (
                        "source_request_id is already associated "
                        "with a different employee or account"
                    ),
                },
            )

        if record.status == "IN_PROGRESS":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "request_in_progress",
                    "message": (
                        "This offboarding request is already being processed"
                    ),
                },
            )

        if record.response_json is None or record.response_status is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "request_result_unavailable",
                    "message": (
                        "This request has an audit record but no stored "
                        "response; reconcile it before retrying"
                    ),
                },
            )

        cached_response = json.loads(record.response_json)
        if record.response_status >= 400:
            raise HTTPException(
                status_code=record.response_status,
                detail=cached_response.get(
                    "detail",
                    cached_response,
                ),
            )
        _save_mail_offboarding_audit(
            source_request,
            cached_response,
        )
        return cached_response

    try:
        plan = workflow_runtime.run_plan_engine(
            adapter=employee_offboarding_api_adapter,
            source_data=source_data,
        )
    except ValueError as ex:
        offboarding_audit_repository.complete(
            audit_id=record.id,
            status="FAILED",
            response={"detail": str(ex)},
            response_status=400,
            actual_account=requested_account,
        )
        raise
    except Exception as ex:
        offboarding_audit_repository.complete(
            audit_id=record.id,
            status="FAILED",
            response={"detail": str(ex)},
            response_status=500,
            actual_account=requested_account,
        )
        raise

    result = {
        "success": True,
        "request_id": plan.request_id,
        "workflow_id": plan.workflow_id,
        "execute_at": plan.execute_at,
    }
    offboarding_audit_repository.complete(
        audit_id=record.id,
        status="SCHEDULED",
        response=result,
        response_status=200,
        actual_account=requested_account,
    )
    parsed_request.request_id = plan.request_id
    access_snapshot_service.save_snapshot(parsed_request)

    _save_mail_offboarding_audit(
        source_request,
        result,
    )
    return result


@router.post(
    "/employee-offboarding"
)
def employee_offboarding(
    source_request:
        EmployeeOffboardingApiRequest,
):

    try:

        return create_offboarding_plan(
            source_request
        )

    except HTTPException:

        raise

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
    "/ra_soat/analyze"
)
async def analyze_offboarding_file(
    file: UploadFile = File(...),
):
    temp_file_path = None

    try:
        file_extension = os.path.splitext(
            file.filename or ""
        )[1].lower()

        if file_extension not in [
            ".xlsx",
            ".xls",
        ]:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Chỉ chấp nhận file Excel "
                    "định dạng .xlsx hoặc .xls"
                ),
            )

        file_content = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
        ) as temp_file:
            temp_file.write(
                file_content
            )

            temp_file_path = (
                temp_file.name
            )

        df = load_excel(
            temp_file_path
        )

        validate_headers(df)

        df["Mail nội bộ"] = (
            df["Mail nội bộ"]
            .apply(normalize_email)
        )

        df["Username"] = (
            df["Mail nội bộ"]
            .apply(extract_username)
        )

        users = map_dataframe_to_source_users(
            df
        )
        requests, discovery_results = (
            discover_users_and_build_requests(
                users
            )
        )

        found_accounts = [
            result
            for result in discovery_results
            if result.found
        ]

        already_disabled = [
            result
            for result in discovery_results
            if (
                result.found
                and result.is_disabled is True
            )
        ]

        active_missing_email = [
            result
            for result in discovery_results
            if (
                result.found
                and result.is_disabled is False
                and not result.email
            )
        ]

        no_related_accounts = len(
            [
                x
                for x in discovery_results
                if not x.found
            ]
        )

        unknown_status = [
            result
            for result in discovery_results
            if (
                result.found
                and result.is_disabled is None
            )
        ]
        created_at = (
            datetime
            .now(
                timezone.utc
            )
            .isoformat()
        )

        session_id = None

        if requests:

            session_id = (
                create_review_session_id()
            )

            request_candidates = [
                request.model_dump()
                for request in requests
            ]

            review_session = {

                "session_id":
                    session_id,

                "file_name":
                    file.filename,

                "source":
                    "RA_SOAT_OFFBOARDING",

                "status":
                    "READY_FOR_CONFIRM",

                "created_at":
                    created_at,

                "request_candidates":
                    request_candidates,

                "confirmation": {
                    "confirmed_at": None,
                    "created_requests": [],
                },
            }

            review_session_repository.save(
                review_session
            )

        return {
            "success": True,
            "file_name": file.filename,
            "session_id":
                session_id,

            "totalUsers":
                len(users),

            "totalSearchKeys":
                len(discovery_results),

            "foundAccounts":
                len(found_accounts),

            "alreadyDisabled":
                len(already_disabled),

            "missingEmail":
                len(active_missing_email),

            "unknownStatus":
                len(unknown_status),

            "noRelatedAccounts": no_related_accounts,

            "requestsReady":
                len(requests),

            "results": [
                {
                    "searchKey":
                        result.search_key,

                    "found":
                        result.found,

                    "samAccountName":
                        result.sam_account_name,

                    "email":
                        result.email,

                    "isDisabled":
                        result.is_disabled,
                }
                for result in discovery_results
            ],
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Không thể đọc file Excel: "
                f"{str(exc)}"
            ),
        )

    finally:
        if (
            temp_file_path
            and os.path.exists(
                temp_file_path
            )
        ):
            os.remove(
                temp_file_path
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

    for candidate_index, candidate in enumerate(
        session["request_candidates"]
    ):
        source_data = dict(candidate)
        source_data["source_type"] = "EXCEL"
        source_data["source_request_id"] = (
            f"OFFBOARDING-EXCEL-{request.session_id}-"
            f"{candidate_index}"
        )
        source_request = EmployeeOffboardingApiRequest.model_validate(
            source_data
        )
        create_offboarding_plan(source_request)

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
    
    journal_repository = (
        WorkflowJournalRepository()
    )

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

    journal_repository.save(
        workflow_name=(
            request.workflowInfo.get(
                "workflowName",
                "Untitled Workflow"
            )
        ),
        created_by="sonnm",
        snapshot=request.model_dump()
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
    journal_repository = (
            WorkflowJournalRepository()
        )
    workflow_id = (
        request.workflowInfo.get(
            "workflowId"
        )
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

    
    journal_updated = journal_repository.mark_executed(workflow_id)

    if not journal_updated:
        raise HTTPException(
            status_code=500,
            detail=(
                "Workflow plans were created, "
                "but journal status could not "
                "be updated to executed."
            )
        )


    return {
            "success": True,
            "requestCount": len(requests),
            "planCount": len(created_plans),
            "plans": created_plans
        }

    



@router.get(
    "/custom-workflow/journal"
)
def get_workflow_journal():

    journal_repository = (
        WorkflowJournalRepository()
    )

    entries = (
        journal_repository.list_by_user(
            "sonnm"   # tạm thời
        )
    )

    return {
        "success": True,
        "items": entries
    }
        
@router.get(
    "/custom-workflow/journal/{journal_id}"
)
def get_workflow_journalid(
    journal_id: str,

):
    repository = WorkflowJournalRepository()

    entry = repository.get_by_id(
        journal_id
    )

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Workflow journal not found"
        )

    return {
        "success": True,
        "item": entry
    }

@router.delete(
    "/custom-workflow/journal/{journal_id}"
)
def delete_workflow_journal(
    journal_id: str,
):
    repository = WorkflowJournalRepository()

    entry = repository.get_by_id(
        journal_id
    )

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Workflow journal not found"
        )

    if entry.get("status") == "executed":
        raise HTTPException(
            status_code=400,
            detail=(
                "Workflow này đã được thực thi. "
                "Workflow sẽ được tự động dọn dẹp "
                "theo chính sách cleanup của hệ thống."
            )
        )

    workflow_id = entry.get(
        "workflow_id"
    )

    repository.delete_registry_workflow(
        workflow_id
    )

    deleted = repository.delete(
        journal_id
    )

    return {
        "success": True,
        "deleted": deleted
    }

@router.post(
    "/temp-access"
)
def execute_temp_access(
    payload: Dict[str, Any]
):

    adapter = (
        TargetObjectWithNewValueAdapter()
    )

    plan = (
        workflow_runtime.run_plan_engine(
            adapter=adapter,
            source_data=payload,
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

        "message":
            (
                "Temporary Access "
                "workflow created"
            ),
    }


@router.post(
    "/temp-resolve-object"
)
def temp_resolve_object(
    request: TempResolveObjectRequest
):
    def get_display_name(
        item: dict,
    ) -> str:

        return (
            item.get("ou")
            or item.get("group_name")
            or item.get("name")
            or "Unknown"
        )

    keyword = (
        request.keyword
        .strip()
    )

    if not keyword:

        raise HTTPException(
            status_code=400,
            detail="keyword is required"
        )

    object_type = (
        request.object_type
        .upper()
        .strip()
    )

    if object_type == "OU":

        result = search_ou(
            connection=ldap.connection,
            keyword=keyword,
        )

    elif object_type == "GROUP":

        result = search_group(
            connection=ldap.connection,
            keyword=keyword,
        )

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported object type: "
                f"{object_type}"
            )
        )


    matches = (
        result.get(
            "results",
            []
        )
    )

    if not matches:

        return {
            "resolved": False,

            "message":
                "Object not found",
        }

    if len(matches) == 1:

        return {
            "resolved": True,

            "distinguished_name":
                matches[0][
                    "distinguished_name"
                ],
        }

    return {
        "resolved": False,

        "multiple": True,

        "results": [
            {
                "name":
                    get_display_name(
                        item
                    ),

                "distinguished_name":
                    item[
                        "distinguished_name"
                    ],
            }
            for item in matches
        ],
    }