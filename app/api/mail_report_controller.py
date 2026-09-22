from datetime import datetime
from datetime import timedelta

from fastapi import APIRouter
from fastapi import HTTPException

from app.auto_engine.report.mail_request_report_service import (
    MailRequestReportService,
)

router = APIRouter()

report_service = (
    MailRequestReportService()
)

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

    return {

        "success": True,

        "report_type":
            "daily",

        "file_name":
            filename,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL - HÀNG NGÀY"
            ),

        "csv_content":
            report_service
            .export_csv_content(
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

    return {

        "success": True,

        "report_type":
            "weekly",

        "file_name":
            filename,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL - HÀNG TUẦN"
            ),

        "csv_content":
            report_service
            .export_csv_content(
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
    "/mail-report/monthly/export"
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

    return {

        "success": True,

        "file_name":
            filename,

        "body":
            report_service.to_text(
                report,
                "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL"
            ),

        "csv_content":
            report_service
            .export_csv_content(
                report
            )
    }