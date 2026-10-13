from datetime import datetime

from app.auto_engine.sqlite.onboarding_audit_repository import (
    OnboardingAuditRepository,
)


class OnboardingAudit:
    def __init__(
        self,
        source_request_id: str,
        employee_id: str,
        requested_account: str,
        repository: OnboardingAuditRepository | None = None,
        audit_id: int | None = None,
        defer_finish: bool = False,
    ):
        self.repository = repository or OnboardingAuditRepository()
        if audit_id is None:
            self.audit_id = self.repository.start(
                source_request_id=source_request_id,
                employee_id=employee_id,
                requested_account=requested_account,
            )
        else:
            self.audit_id = audit_id
        self.defer_finish = defer_finish
        self._actual_account = None

    def set_actual_account(self, actual_account: str) -> None:
        self._actual_account = actual_account

    def record_step(
        self,
        step_name: str,
        success: bool,
        started_at: datetime,
        completed_at: datetime,
        details: dict | None = None,
    ) -> None:
        self.repository.record_step(
            audit_id=self.audit_id,
            step_name=step_name,
            success=success,
            started_at=started_at,
            completed_at=completed_at,
            details=details,
        )

    def finish(self, status: str) -> None:
        if self.defer_finish:
            return

        self.repository.finish(
            audit_id=self.audit_id,
            status=status,
            actual_account=self._actual_account,
        )

    def complete(
        self,
        status: str,
        response: dict,
        response_status: int,
    ) -> None:
        self.repository.complete(
            audit_id=self.audit_id,
            status=status,
            response=response,
            response_status=response_status,
            actual_account=self._actual_account,
        )
