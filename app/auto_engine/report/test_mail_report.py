from datetime import datetime
from datetime import timedelta

from app.auto_engine.report.mail_request_report_service import (
    MailRequestReportService,
)


def main():

    service = (
        MailRequestReportService()
    )

    end_date = (
        datetime.now()
    )

    start_date = (
        end_date
        - timedelta(days=30)
    )

    report = (
        service.generate(
            start_date,
            end_date,
        )
    )

    print(
        service.to_text(
            report,
            "BÁO CÁO XỬ LÝ YÊU CẦU TỪ EMAIL"
        )
    )

    service.export_csv(

        report,

        "mail_report.csv"
    )

    print()

    print(
        "CSV exported:"
        " mail_report.csv"
    )


if __name__ == "__main__":
    main()