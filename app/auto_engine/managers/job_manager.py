from datetime import datetime
from typing import List

from app.auto_engine.models.job import (
    Job,
    JobStatus,
)
from app.auto_engine.services.job_repository import (
    JobRepository,
)


class JobManager:

    def __init__(
        self,
        job_repository: JobRepository,
    ):
        self.job_repository = (
            job_repository
        )

    def update(
        self,
    ) -> None:
        """
        Dành cho retry và recovery ở CP sau.
        """
        pass

    def claim_executable_jobs(
        self,
        limit: int = 1,
    ) -> List[Job]:
        """
        Chỉ claim Job khi:

        - PENDING
        - đã đến execute_at
        - tất cả dependency COMPLETED

        V1 claim tối đa 1 Job mỗi cycle để
        dễ kiểm soát E2E và tránh claim hàng loạt.
        """

        pending_jobs = (
            self.job_repository
            .list_by_status(
                JobStatus.PENDING
            )
        )

        pending_jobs = sorted(
            pending_jobs,
            key=lambda job: (
                job.execute_at,
                job.created_at,
                job.job_id,
            ),
        )

        claimed_jobs: List[Job] = []

        for job in pending_jobs:

            if len(claimed_jobs) >= limit:
                break

            if not self._is_due(
                job
            ):
                continue

            if not self._dependencies_completed(
                job
            ):
                continue

            self.mark_running(
                job
            )

            claimed_jobs.append(
                job
            )

        return claimed_jobs

    def mark_running(
        self,
        job: Job,
    ) -> Job:

        if job.status != JobStatus.PENDING:
            raise ValueError(
                "Chỉ Job PENDING mới được "
                "chuyển sang RUNNING. "
                f"job_id={job.job_id}, "
                f"status={job.status}"
            )

        job.status = JobStatus.RUNNING

        if job.started_at is None:
            job.started_at = datetime.now()

        job.completed_at = None
        job.result_message = None
        job.error_message = None

        return self.job_repository.save(
            job
        )

    def mark_completed(
        self,
        job: Job,
        message: str = "",
    ) -> Job:

        if job.status != JobStatus.RUNNING:
            raise ValueError(
                "Chỉ Job RUNNING mới được "
                "chuyển sang COMPLETED. "
                f"job_id={job.job_id}, "
                f"status={job.status}"
            )

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now()
        job.result_message = message
        job.error_message = None

        return self.job_repository.save(
            job
        )

    def mark_failed(
        self,
        job: Job,
        error: str = "",
    ) -> Job:

        if job.status != JobStatus.RUNNING:
            raise ValueError(
                "Chỉ Job RUNNING mới được "
                "chuyển sang FAILED. "
                f"job_id={job.job_id}, "
                f"status={job.status}"
            )

        job.status = JobStatus.FAILED
        job.completed_at = datetime.now()
        job.result_message = None
        job.error_message = error

        return self.job_repository.save(
            job
        )

    @staticmethod
    def _is_due(
        job: Job,
    ) -> bool:

        now = datetime.now()

        job_execute_at = job.execute_at

        if (
            job_execute_at.tzinfo is not None
            and now.tzinfo is None
        ):
            now = now.astimezone(
                job_execute_at.tzinfo
            )

        return job_execute_at <= now

    def _dependencies_completed(
        self,
        job: Job,
    ) -> bool:

        dependency_ids = (
            job.depends_on or []
        )

        if not dependency_ids:
            return True

        jobs_in_request = (
            self.job_repository
            .list_by_request_id(
                job.request_id
            )
        )

        jobs_by_action_id = {
            item.action_id: item
            for item in jobs_in_request
        }

        for dependency_action_id in (
            dependency_ids
        ):
            dependency_job = (
                jobs_by_action_id.get(
                    dependency_action_id
                )
            )

            if dependency_job is None:
                return False

            if (
                dependency_job.status
                != JobStatus.COMPLETED
            ):
                return False

        return True