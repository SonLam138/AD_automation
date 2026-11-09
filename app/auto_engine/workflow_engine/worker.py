import json
import traceback
from datetime import datetime
from typing import Any, Dict

from app.auto_engine.actions.ad_actions import (
    AdActionRegistry,
)
from app.auto_engine.managers.job_manager import (
    JobManager,
)
from app.auto_engine.models.job import (
    Job,
    JobStatus,
)
from app.auto_engine.sqlite.offboarding_audit_repository import (
    OffboardingAuditRepository,
)


class Worker:

    def __init__(
        self,
        job_manager: JobManager,
        action_registry:
            AdActionRegistry,
    ):
        self.job_manager = job_manager

        self.action_registry = (
            action_registry
        )
        self.offboarding_audit_repository = (
            OffboardingAuditRepository()
        )

    def update(
        self,
    ) -> None:
        """
        Một Worker cycle:

        JobManager:
            PENDING -> RUNNING

        Worker:
            Action execute

        JobManager:
            RUNNING -> COMPLETED/FAILED
        """

        jobs = (
            self.job_manager
            .claim_executable_jobs(
                limit=1
            )
        )

        for job in jobs:
            self._execute_job(
                job
            )

    def _execute_job(
        self,
        job: Job,
    ) -> None:

        print(
            "[Worker] Execute job: "
            f"{job.job_id} "
            f"action={job.action_code}"
        )

        try:
            action = (
                self.action_registry.get(
                    job.action_code
                )
            )

            execution_context = {
                "job_id": job.job_id,
                "request_id":
                    job.request_id,
                "workflow_id":
                    job.workflow_id,
                "action_id":
                    job.action_id,
                "action_code":
                    job.action_code,
                "execution_source":
                    "WORKER",
            }

            result = action.execute(
                business_data=(
                    job.business_data
                ),
                execution_context=(
                    execution_context
                ),
            )

            if not self._is_success(
                result
            ):
                error_message = (
                    self._get_error_message(
                        result
                    )
                )

                self.job_manager.mark_failed(
                    job=job,
                    error=error_message,
                )
                self._record_offboarding_step(
                    job=job,
                    success=False,
                    details={
                        "error": error_message,
                    },
                )

                print(
                    "[Worker] Job failed: "
                    f"{job.job_id}, "
                    f"error={error_message}"
                )

                return

            result_message = (
                self._serialize_result(
                    result
                )
            )

            self.job_manager.mark_completed(
                job=job,
                message=result_message,
            )
            self._record_offboarding_step(
                job=job,
                success=True,
                details={
                    "result": result,
                },
            )

            print(
                "[Worker] Job completed: "
                f"{job.job_id}"
            )

        except Exception as ex:

            try:
                if job.status == JobStatus.RUNNING:
                    self.job_manager.mark_failed(
                        job=job,
                        error=str(ex),
                    )

                if job.status == JobStatus.FAILED:
                    self._record_offboarding_step(
                        job=job,
                        success=False,
                        details={
                            "error": job.error_message or str(ex),
                        },
                    )

            except Exception:
                print(
                    "[Worker] Failed to update "
                    "Job status: "
                    f"{job.job_id}"
                )

                traceback.print_exc()

            print(
                "[Worker] Job execution "
                "failed: "
                f"{job.job_id}"
            )

            traceback.print_exc()

    def _record_offboarding_step(
        self,
        job: Job,
        success: bool,
        details: dict,
    ) -> None:
        if not job.workflow_id.startswith("OFFBOARDING_"):
            return

        source_request_id = job.business_data.get(
            "source_request_id"
        )
        if not source_request_id:
            raise RuntimeError(
                "Offboarding job is missing source_request_id: "
                f"request_id={job.request_id}, action_id={job.action_id}"
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

        started_at = job.started_at or job.created_at
        completed_at = job.completed_at or datetime.utcnow()
        self.offboarding_audit_repository.record_step(
            audit_id=audit_record.id,
            step_name=job.action_code,
            success=success,
            started_at=started_at,
            completed_at=completed_at,
            details=details,
        )

    @staticmethod
    def _is_success(
        result: Any,
    ) -> bool:

        if isinstance(
            result,
            dict,
        ):
            return result.get(
                "success"
            ) is True

        if isinstance(
            result,
            bool,
        ):
            return result

        return result is not None

    @staticmethod
    def _get_error_message(
        result: Any,
    ) -> str:

        if isinstance(
            result,
            dict,
        ):
            return str(
                result.get(
                    "error"
                )
                or result.get(
                    "message"
                )
                or result
            )

        return (
            "AD Action trả về kết quả "
            "không thành công"
        )

    @staticmethod
    def _serialize_result(
        result: Any,
    ) -> str:

        if isinstance(
            result,
            dict,
        ):
            return json.dumps(
                result,
                ensure_ascii=False,
                default=str,
            )

        return str(result)
