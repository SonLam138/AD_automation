from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)
from app.auto_engine.models.job import (
    JobStatus,
)
from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)
from app.auto_engine.services.job_repository import (
    JobRepository,
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
            active_execution
        )

    def _update_execution_status(
        self,
        active_execution: ActiveExecution,
    ) -> None:

        total_actions = len(
            active_execution.actions
        )

        completed_count = len(
            active_execution.completed_action_ids
        )

        failed_count = len(
            active_execution.failed_action_ids
        )

        #
        # COMPLETED
        #
        if (
            total_actions > 0
            and
            completed_count == total_actions
        ):
            active_execution.status = (
                ActiveExecutionStatus.COMPLETED
            )
            return

        #
        # FAILED
        #
        if failed_count > 0:
            active_execution.status = (
                ActiveExecutionStatus.FAILED
            )
            return

        #
        # RUNNING
        #
        if (
            active_execution.current_action_id
            is not None
        ):
            active_execution.status = (
                ActiveExecutionStatus.RUNNING
            )
            return

        #
        # JOB_CREATED
        #
        has_jobs = (
            completed_count > 0
            or
            failed_count > 0
            or
            self.job_repository
            .list_by_request_id(
                active_execution.request_id
            )
        )

        if has_jobs:
            active_execution.status = (
                ActiveExecutionStatus.JOB_CREATED
            )
            return

    def _should_cleanup(
        self,
        active_execution: ActiveExecution,
    ) -> bool:

        return active_execution.status in [
            ActiveExecutionStatus.COMPLETED,
            ActiveExecutionStatus.FAILED,
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