from app.auto_engine.report.mail_request_report_service import (
    MailRequestReportService,
)


class HRRequestAuditRepositoryStub:
    def get_scheduled_source_request_ids(self, source_request_ids):
        stored_ids = {
            "mail-1",
            "mail-4",
        }
        return sorted(stored_ids.intersection(source_request_ids))


class WorkflowAuditRepositoryMustNotBeRead:
    def get_plan_responses_by_source_request_ids(self, _source_request_ids):
        raise AssertionError(
            "Plan status must be sourced from HR_request_audits only."
        )


def test_plan_status_is_read_only_from_hr_request_audit_repository():
    service = MailRequestReportService.__new__(MailRequestReportService)
    service.repository = HRRequestAuditRepositoryStub()
    service.onboarding_repository = WorkflowAuditRepositoryMustNotBeRead()
    service.offboarding_repository = WorkflowAuditRepositoryMustNotBeRead()

    scheduled_ids = service.get_plan_scheduled_source_request_ids(
        ["mail-1", "mail-2", "mail-4", "mail-unknown"]
    )

    assert scheduled_ids == ["mail-1", "mail-4"]
