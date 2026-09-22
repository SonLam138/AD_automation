from datetime import datetime, timedelta
import csv
import io

from app.auto_engine.report.mail_request_report import (
    MailRequestReport,
)

from app.auto_engine.sqlite.mail_request_audit_repository import (
    MailRequestAuditRepository,
)


class MailRequestReportService:

    def __init__(
        self,
    ):

        self.repository = (
            MailRequestAuditRepository()
        )

    WORKFLOW_DISPLAY_NAMES = {

        "OFFBOARDING_RESIGNED":
            "Đóng tài khoản nhân sự nghỉ việc",

        "OFFBOARDING_LONG_LEAVE":
            "Đóng tài khoản nhân sự nghỉ dài hạn",

        "OFFBOARDING_SUSPENDED":
            "Đóng tài khoản nhân sự bị đình chỉ",

        "TEMP_ACCESS_USER":
            "Cấp quyền truy cập tạm thời",

        "GROUP_ACCESS":
            "Cấp quyền nhóm người dùng",

        "SHARED_MAILBOX":
            "Cấp quyền hộp thư dùng chung",
    }


    def get_workflow_display_name(
        self,
        workflow_id: str,
    ) -> str:

        return (
            self.WORKFLOW_DISPLAY_NAMES.get(
                workflow_id,
                workflow_id,
            )
        )

    def generate(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> MailRequestReport:

        return (
            MailRequestReport(

                period_start=start_date,

                period_end=end_date,

                total_requests=
                    self.repository
                    .count_between(
                        start_date,
                        end_date,
                    ),

                emergency_requests=
                    self.repository
                    .count_emergency_between(
                        start_date,
                        end_date,
                    ),

                workflow_summary=
                    self.repository
                    .group_by_workflow(
                        start_date,
                        end_date,
                    ),

                reason_summary=
                    self.repository
                    .group_by_reason(
                        start_date,
                        end_date,
                    ),

                details=
                    self.repository
                    .get_between(
                        start_date,
                        end_date,
                    ),
            )
        )

    def to_text(
        self,
        report: MailRequestReport,
        title: str,
    ) -> str:

        lines = []

        lines.append(title)

        lines.append(
            "=" * 60
        )

        lines.append(
            "Kỳ báo cáo:"
        )

        lines.append(
            f"Từ: "
            f"{report.period_start:%d/%m/%Y %H:%M}"
        )

        lines.append(
            f"Đến: "
            f"{report.period_end:%d/%m/%Y %H:%M}"
        )

        lines.append("")

        lines.append(
            f"Tổng số yêu cầu tiếp nhận: "
            f"{report.total_requests}"
        )

        lines.append(
            f"Số yêu cầu khẩn cấp: "
            f"{report.emergency_requests}"
        )

        lines.append("")

        lines.append(
            "Phân loại theo nghiệp vụ"
        )

        lines.append(
            "-" * 60
        )

        for item in (
            report.workflow_summary
        ):

            lines.append(

                f"{self.get_workflow_display_name(item['workflow_id'])}: "

                f"{item['total']}"
            )

        lines.append("")

        lines.append(
            "Phân loại theo lý do"
        )

        lines.append(
            "-" * 60
        )

        for item in (
            report.reason_summary
        ):

            lines.append(
                f"{item['reason']}: "
                f"{item['total']}"
            )

        lines.append("")

        lines.append(
            "Thông tin chi tiết được đính kèm theo email."
        )

        return "\n".join(
            lines
        )

    def export_csv(
        self,
        report: MailRequestReport,
        output_file: str,
    ):

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csvfile:

            writer = csv.writer(
                csvfile
            )

            writer.writerow(
                [
                    "request_id",
                    "workflow_id",
                    "employee_id",
                    "email",
                    "reason",
                    "sender",
                    "subject",
                    "is_emergency",
                    "created_at",
                ]
            )

            for item in (
                report.details
            ):

                writer.writerow(
                    [
                        item.request_id,
                        item.workflow_id,
                        item.employee_id,
                        item.email,
                        item.reason,
                        item.sender,
                        item.subject,
                        item.is_emergency,
                        item.created_at,
                    ]
                )


    def generate_daily_report(
        self,
    ) -> MailRequestReport:

        now = datetime.now()

        start_date = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
        )

        return self.generate(
            start_date=start_date,
            end_date=now,
        )

    def generate_weekly_report(
        self,
    ) -> MailRequestReport:

        now = datetime.now()

        start_date = (
            now
            - timedelta(
                days=7
            )
        )

        return self.generate(
            start_date=start_date,
            end_date=now,
        )

    def generate_monthly_report(
        self,
    ) -> MailRequestReport:

        now = datetime.now()

        start_date = (
            now
            - timedelta(
                days=30
            )
        )

        return self.generate(
            start_date=start_date,
            end_date=now,
        )

    def generate_custom_report(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> MailRequestReport:

        return self.generate(
            start_date=start_date,
            end_date=end_date,
        )

    def export_csv_content(
        self,
        report: MailRequestReport,
    ) -> str:

        output = io.StringIO()

        writer = csv.writer(
            output
        )

        writer.writerow(
            [
                "request_id",
                "workflow_id",
                "employee_id",
                "email",
                "reason",
                "sender",
                "subject",
                "is_emergency",
                "created_at",
            ]
        )

        for item in report.details:

            writer.writerow(
                [
                    item.request_id,
                    item.workflow_id,
                    item.employee_id,
                    item.email,
                    item.reason,
                    item.sender,
                    item.subject,
                    item.is_emergency,
                    item.created_at,
                ]
            )

        return output.getvalue()