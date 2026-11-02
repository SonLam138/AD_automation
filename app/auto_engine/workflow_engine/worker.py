import json
import traceback
from typing import Any, Dict

from app.auto_engine.actions.ad_actions import (
    AdActionRegistry,
)
from app.auto_engine.managers.job_manager import (
    JobManager,
)
from app.auto_engine.models.job import (
    Job,
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

            print(
                "[Worker] Job completed: "
                f"{job.job_id}"
            )

        except Exception as ex:

            try:
                self.job_manager.mark_failed(
                    job=job,
                    error=str(ex),
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
