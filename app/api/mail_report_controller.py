from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import require_service_token
from app.auto_engine.report.mail_request_report_service import (
    MailRequestReportService,
)

router = APIRouter()

report_service = (
    MailRequestReportService()
)


class PlanStatusRequest(BaseModel):
    source_request_ids: list[str]


class ManualReportExportRequest(BaseModel):
    report_type: str
    period_start: datetime
    period_end: datetime


@router.post(
    "/manual/export"
)
def export_manual_report(
    request: ManualReportExportRequest,
    claims=Depends(require_service_token),
):
    if request.report_type not in {
        "daily",
        "weekly",
        "monthly",
        "manual",
    }:
        raise HTTPException(
            status_code=422,
            detail=(
                "report_type must be daily, weekly, monthly, or manual."
            ),
        )
    if request.period_start > request.period_end:
        raise HTTPException(
            status_code=422,
            detail="period_start must be earlier than or equal to period_end.",
        )

    report = report_service.generate(
        start_date=request.period_start,
        end_date=request.period_end,
    )
    period_label = (
        f"{request.period_start:%Y%m%d_%H%M%S}_"
        f"{request.period_end:%Y%m%d_%H%M%S}"
    )
    return {
        "success": True,
        "report_type": request.report_type,
        "file_name": f"mail_{request.report_type}_{period_label}.csv",
        "onboarding_file_name": (
            f"onboarding_{request.report_type}_{period_label}.csv"
        ),
        "offboarding_file_name": (
            f"offboarding_{request.report_type}_{period_label}.csv"
        ),
        "body": report_service.to_text(
            report,
            "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL",
        ),
        "csv_content": report_service.export_csv_content(report),
        "onboarding_csv_content":
            report_service.export_onboarding_csv_content(report),
        "offboarding_csv_content":
            report_service.export_offboarding_csv_content(report),
    }


@router.get(
    "/daily/export"
)
def export_daily_report():

    report = (
        report_service
        .generate_daily_report()
    )

    filename = (
        f"mail_daily_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )
    onboarding_filename = (
        f"onboarding_daily_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )
    offboarding_filename = (
        f"offboarding_daily_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )
    return {

        "success": True,

        "report_type":
            "daily",

        "file_name":
            filename,

        "onboarding_file_name": onboarding_filename,

        "offboarding_file_name": offboarding_filename,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL - HÀNG NGÀY"
            ),

        "csv_content":
            report_service
            .export_csv_content(
                report
            ),
        "onboarding_csv_content":
            report_service
            .export_onboarding_csv_content(
            report
            ),

        "offboarding_csv_content":
            report_service
            .export_offboarding_csv_content(
                report
            )
    }

@router.get(
    "/weekly/export"
)
def export_weekly_report():

    report = (
        report_service
        .generate_weekly_report()
    )

    filename = (
        f"mail_weekly_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )
    onboarding_filename = (
            f"onboarding_weekly_report_"
            f"{datetime.now():%Y%m%d}.csv"
        )
    offboarding_filename = (
        f"offboarding_weekly_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )

    return {

        "success": True,

        "report_type":
            "weekly",

        "file_name":
            filename,

        "onboarding_file_name": onboarding_filename,

        "offboarding_file_name": offboarding_filename,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL - HÀNG TUẦN"
            ),

        "csv_content":
            report_service
            .export_csv_content(
                report
            ),
        "onboarding_csv_content":
            report_service
            .export_onboarding_csv_content(
            report
            ),

        "offboarding_csv_content":
            report_service
            .export_offboarding_csv_content(
                report
            )
    }

@router.get(
    "/monthly"
)
def monthly_report():

    report = (
        report_service
        .generate_monthly_report()
    )

    return {

        "report_type":
            "monthly",

        "period_start":
            report.period_start,

        "period_end":
            report.period_end,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL - HÀNG THÁNG"
            )
    }

@router.get(
    "/monthly/export"
)
def export_monthly_report():

    report = (
        report_service
        .generate_monthly_report()
    )

    filename = (
        f"mail_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )
    onboarding_filename = (
        f"onboarding_monthly_report_"
        f"{datetime.now():%Y%m%d}.csv"
        )
    offboarding_filename = (
        f"offboarding_monthly_report_"
        f"{datetime.now():%Y%m%d}.csv"
    )

    return {

        "success": True,

        "file_name":
            filename,

        "onboarding_file_name": onboarding_filename,

        "offboarding_file_name": offboarding_filename,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL"
            ),

        "csv_content":
            report_service
            .export_csv_content(
                report
            ),
        "onboarding_csv_content":
            report_service
            .export_onboarding_csv_content(
            report
            ),

        "offboarding_csv_content":
            report_service
            .export_offboarding_csv_content(
                report
            )
    }


@router.post(
    "/plan-status"
)
def get_plan_status(
    request: PlanStatusRequest,
    claims=Depends(require_service_token),
):
    if len(request.source_request_ids) > 5000:
        raise HTTPException(
            status_code=413,
            detail="At most 5000 source request IDs can be queried at once.",
        )

    source_request_ids = list(
        dict.fromkeys(
            source_request_id.strip()
            for source_request_id in request.source_request_ids
            if source_request_id.strip()
        )
    )
    return {
        "scheduled_source_request_ids":
            report_service.get_plan_scheduled_source_request_ids(
                source_request_ids
            )
    }