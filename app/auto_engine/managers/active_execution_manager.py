import json
from datetime import datetime

from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)
from app.auto_engine.models.job import (
    Job,
    JobStatus,
)
from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)
from app.auto_engine.services.job_repository import (
    JobRepository,
)
from app.auto_engine.sqlite.offboarding_audit_repository import (
    OffboardingAuditRepository,
)


class ActiveExecutionManager:

    def __init__(
        self,
        active_execution_repository: ActiveExecutionRepository,
        job_repository: JobRepository,
    ):
        self.active_execution_repository = (
            active_execution_repository
        )

        self.job_repository = (
            job_repository
        )
        self.offboarding_audit_repository = (
            OffboardingAuditRepository()
        )

    def update(
        self,
    ) -> None:

        active_executions = (
            self.active_execution_repository
            .list_active()
        )

        for active_execution in active_executions:

            self._update_execution(
                active_execution
            )
            self._finalize_offboarding_audit(
                active_execution
            )
            print(
                "[DEBUG]",
                active_execution.request_id,
                active_execution.status
                )

            if self._should_cleanup(
                active_execution
            ):

                self._cleanup(
                    active_execution
                )

                continue

            self.active_execution_repository.save(
                active_execution
            )

    def _finalize_offboarding_audit(
        self,
        active_execution: ActiveExecution,
    ) -> None:
        if not active_execution.workflow_id.startswith("OFFBOARDING_"):
            return

        if active_execution.status not in {
            ActiveExecutionStatus.COMPLETED,
            ActiveExecutionStatus.COMPLETED_WITH_ERRORS,
            ActiveExecutionStatus.FAILED,
            ActiveExecutionStatus.CANCELLED,
        }:
            return

        source_request_id = active_execution.business_data.get(
            "source_request_id"
        )
        if not source_request_id:
            raise RuntimeError(
                "Offboarding execution is missing source_request_id: "
                f"request_id={active_execution.request_id}"
            )

        audit_record = (
            self.offboarding_audit_repository
            .get_by_source_request_id(
                str(source_request_id)
            )
        )
        if audit_record is None:
            raise RuntimeError(
                "Offboarding audit record was not found for "
                f"source_request_id={source_request_id}"
            )
        if audit_record.status in {"SUCCESS", "FAILED"}:
            return

        outcomes = json.loads(
            audit_record.step_outcomes_json or "[]"
        )
        recorded_steps = {
            outcome.get("step")
            for outcome in outcomes
        }
        jobs = self.job_repository.list_by_request_id(
            active_execution.request_id
        )
        completed_at = datetime.utcnow()
        for job in jobs:
            if job.status not in {
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            }:
                continue
            if job.action_code in recorded_steps:
                continue

            details = {
                "action_id": job.action_id,
                "failure_reason": (
                    job.failure_reason.value
                    if job.failure_reason
                    else None
                ),
            }
            if job.error_message:
                details["error"] = job.error_message
            if job.result_message:
                details["result"] = job.result_message

            self.offboarding_audit_repository.record_step(
                audit_id=audit_record.id,
                step_name=job.action_code,
                success=job.status == JobStatus.COMPLETED,
                started_at=job.started_at or job.created_at,
                completed_at=job.completed_at or completed_at,
                details=details,
            )

        target_object = active_execution.business_data.get(
            "target_object",
            {},
        )
        actual_account = target_object.get(
            "sam_account_name"
        )
        final_status = (
            "SUCCESS"
            if active_execution.status
            == ActiveExecutionStatus.COMPLETED
            else "FAILED"
        )
        self.offboarding_audit_repository.finish(
            audit_id=audit_record.id,
            status=final_status,
            actual_account=actual_account,
        )

    def _update_execution(
        self,
        active_execution: ActiveExecution,
    ) -> None:

        jobs = (
            self.job_repository
            .list_by_request_id(
                active_execution.request_id
            )
        )

        completed_action_ids = []
        failed_action_ids = []
        current_action_id = None

        for job in jobs:

            if job.status == JobStatus.COMPLETED:

                completed_action_ids.append(
                    job.action_id
                )

            elif job.status == JobStatus.FAILED:

                failed_action_ids.append(
                    job.action_id
                )

            elif job.status == JobStatus.CANCELLED:

                failed_action_ids.append(
                    job.action_id
                )

            elif job.status == JobStatus.RUNNING:

                current_action_id = (
                    job.action_id
                )

        active_execution.completed_action_ids = (
            completed_action_ids
        )

        active_execution.failed_action_ids = (
            failed_action_ids
        )

        active_execution.current_action_id = (
            current_action_id
        )

        self._update_execution_status(
            active_execution,
            jobs,
        )

    def _update_execution_status(
        self,
        active_execution: ActiveExecution,
        jobs: list[Job],
    ) -> None:

        total_actions = len(
            active_execution.actions
        )

        if total_actions == 0:
            return

        completed_count = len(
            active_execution.completed_action_ids
        )

        jobs_by_action_id = {
            job.action_id: job
            for job in jobs
        }

        if active_execution.current_action_id is not None:
            active_execution.status = ActiveExecutionStatus.RUNNING
            return

        terminal_statuses = {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }
        expected_action_ids = {
            action.id
            for action in active_execution.actions
        }
        all_jobs_terminal = (
            expected_action_ids.issubset(
                jobs_by_action_id
            )
            and all(
                jobs_by_action_id[action_id].status
                in terminal_statuses
                for action_id in expected_action_ids
            )
        )

        if not all_jobs_terminal:
            if jobs:
                active_execution.status = (
                    ActiveExecutionStatus.JOB_CREATED
                )
            return

        if total_actions > 0 and completed_count == total_actions:
            active_execution.status = (
                ActiveExecutionStatus.COMPLETED
            )
            return

        failed_action_ids = set(
            active_execution.failed_action_ids
        )
        tolerated_failure_ids = set()

        for job in jobs:
            if job.status != JobStatus.COMPLETED:
                continue
            if not job.continue_on_error:
                continue

            for dependency_action_id in job.depends_on:
                dependency_job = jobs_by_action_id.get(
                    dependency_action_id
                )
                if (
                    dependency_job is not None
                    and dependency_job.status
                    in {
                        JobStatus.FAILED,
                        JobStatus.CANCELLED,
                    }
                ):
                    tolerated_failure_ids.add(
                        dependency_action_id
                    )

        if (
            failed_action_ids
            and failed_action_ids.issubset(
                tolerated_failure_ids
            )
        ):
            active_execution.status = (
                ActiveExecutionStatus.COMPLETED_WITH_ERRORS
            )
            return

        active_execution.status = ActiveExecutionStatus.FAILED

    def _should_cleanup(
        self,
        active_execution: ActiveExecution,
    ) -> bool:

        return active_execution.status in [
            ActiveExecutionStatus.COMPLETED,
            ActiveExecutionStatus.CANCELLED,
        ]

    def _cleanup(
        self,
        active_execution: ActiveExecution,
    ) -> None:

        print(
            "[ActiveExecutionManager] "
            f"Cleanup execution: "
            f"{active_execution.request_id}"
        )

        deleted_jobs = (
            self.job_repository
            .delete_by_request_id(
                active_execution.request_id
            )
        )

        print(
            "[ActiveExecutionManager] "
            f"Deleted jobs: "
            f"{deleted_jobs}"
        )

        self.active_execution_repository.delete(
            active_execution.request_id
        )

        print(
            "[ActiveExecutionManager] "
            f"Deleted execution: "
            f"{active_execution.request_id}"
        )