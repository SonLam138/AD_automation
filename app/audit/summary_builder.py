from datetime import datetime

from app.models.audit_session_summary import AuditSessionSummary


def build_session_summary(
    context,
    steps
) -> AuditSessionSummary:

    # =====================================================
    # Step statistics
    # =====================================================

    total_steps = len(
        steps
    )

    success_steps = len(
        [
            step
            for step in steps
            if step.status == "SUCCESS"
        ]
    )

    failed_steps = len(
        [
            step
            for step in steps
            if step.status == "FAILED"
        ]
    )

    executed_steps = [
        step.step_name
        for step in steps
    ]

    last_completed_step = None

    for step in reversed(
        steps
    ):
        if step.status == "SUCCESS":

            last_completed_step = (
                step.step_name
            )

            break

    failed_step = next(
        (
            step
            for step in steps
            if step.status == "FAILED"
        ),
        None
    )

    # =====================================================
    # Business summary
    # =====================================================

    business_summary = {

        "case_type":
            context.event_type,

        "employee_id":
            context.requested.employee_id,

        "employee_name":
            context.requested.full_name,

        "department":
            context.requested.department,

        "title":
            context.requested.title,

        "requested_account":
            context.requested.account,

        "actual_account":
            context.actual.account,

        "requested_display_name":
            context.requested.display_name,

        "actual_display_name":
            context.actual.display_name,

        "requested_ou":
            context.requested.ou,

        "actual_ou":
            context.actual.ou_dn,

        "result":
            context.status
    }

    # =====================================================
    # Add group summary from step details
    # =====================================================

    add_groups_step = next(
        (
            step
            for step in steps
            if step.step_name == "add_groups"
        ),
        None
    )

    if add_groups_step and add_groups_step.details:

        business_summary[
            "added_groups"
        ] = add_groups_step.details.get(
            "added_groups",
            []
        )

        business_summary[
            "failed_groups"
        ] = add_groups_step.details.get(
            "failed_groups",
            []
        )

    # =====================================================
    # Technical summary
    # =====================================================

    technical_summary = {

        "total_steps":
            total_steps,

        "success_steps":
            success_steps,

        "failed_steps":
            failed_steps,

        "executed_steps":
            executed_steps,

        "last_completed_step":
            last_completed_step,

        "failure_stage":
            context.failure_stage,

        "execution_time_ms":
            context.duration_ms
    }

    # =====================================================
    # Error summary
    # =====================================================

    error_summary = None

    if failed_step:

        error_summary = {

            "failed_step":
                failed_step.step_name,

            "error_code":
                getattr(
                    failed_step,
                    "error_code",
                    None
                ),

            "error_message":
                getattr(
                    failed_step,
                    "error_message",
                    None
                ),

            "failure_stage":
                context.failure_stage,

            "failure_code":
                context.failure_code,

            "failure_reason":
                context.failure_reason
        }

    # =====================================================
    # Summary category
    # =====================================================

    summary_category = resolve_summary_category(
        context=context,
        failed_step=failed_step
    )

    # =====================================================
    # Return summary
    # =====================================================

    return AuditSessionSummary(

        session_id=
            context.session_id,

        event_category=
            context.event_category,

        event_type=
            context.event_type,

        capability=
            context.capability,

        source_type=
            context.source_type,

        source_id=
            context.source_id,

        approved_by=
            getattr(
                context,
                "approved_by",
                None
            ),

        approved_name=
            getattr(
                context,
                "approved_name",
                None
            ),

        approval_type=
            getattr(
                context,
                "approval_type",
                None
            ),

        approval_time=
            getattr(
                context,
                "approval_time",
                None
            ),

        result=
            context.status,

        summary_category=
            summary_category,

        execution_time_ms=
            context.duration_ms or 0,

        generated_at=
            datetime.utcnow(),

        business_summary=
            business_summary,

        technical_summary=
            technical_summary,

        error_summary=
            error_summary
    )


def resolve_summary_category(
    context,
    failed_step
) -> str:

    if context.status == "SUCCESS":
        return "SUCCESS"

    business_failure_stages = [
        "resolve_request",
        "resolve_identity",
        "resolve_groups",
        "validate_request"
    ]

    if context.failure_stage in business_failure_stages:
        return "BUSINESS_ERROR"

    if failed_step:

        business_error_codes = [
            "32",   # noSuchObject
            "68",   # entryAlreadyExists
            "19"    # constraintViolation
        ]

        error_code = getattr(
            failed_step,
            "error_code",
            None
        )

        if str(
            error_code
        ) in business_error_codes:
            return "BUSINESS_ERROR"

    return "SYSTEM_ERROR"