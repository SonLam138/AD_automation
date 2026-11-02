from datetime import datetime
from typing import Dict, List

from app.auto_engine.models.job import (
    Job,
    JobFailureReason,
    JobStatus,
)
from app.auto_engine.services.job_repository import (
    JobRepository,
)
from app.event.event_emitter import emit_event
from app.event.job_monitor_payload import (build_job_monitor_payload)



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
        jobs_by_request: Dict[str, List[Job]] = {}
        cycles_by_request: Dict[str, Dict[str, List[str]]] = {}

        for job in pending_jobs:

            if len(claimed_jobs) >= limit:
                break

            request_jobs = jobs_by_request.get(
                job.request_id
            )
            if request_jobs is None:
                request_jobs = (
                    self.job_repository.list_by_request_id(
                        job.request_id
                    )
                )
                jobs_by_request[job.request_id] = (
                    request_jobs
                )
                cycles_by_request[job.request_id] = (
                    self._dependency_cycles(
                        request_jobs
                    )
                )

            cycle = cycles_by_request[
                job.request_id
            ].get(job.action_id)
            if cycle is not None:
                self.mark_dependency_failed(
                    job=job,
                    error=(
                        "Dependency cycle detected: "
                        + " -> ".join(cycle + [cycle[0]])
                    ),
                )
                request_jobs[:] = [
                    item
                    for item in request_jobs
                    if item.action_id != job.action_id
                ]
                request_jobs.append(job)
                continue

            if not self._is_due(
                job
            ):
                continue

            dependency_state, error = (
                self._get_dependency_state(
                    job,
                    request_jobs,
                )
            )

            if error is not None:
                self.mark_dependency_failed(
                    job=job,
                    error=error,
                )
                request_jobs[:] = [
                    item
                    for item in request_jobs
                    if item.action_id != job.action_id
                ]
                request_jobs.append(job)
                continue

            if not dependency_state:
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
        job.failure_reason = None

        saved_job = (
            self.job_repository.save(
                job
            )
        )

        emit_event(
            event_name=
                "JOB_STARTED",

            source=
                "WORKFLOW_ENGINE",

            job_id=
                saved_job.job_id,
        )

        return saved_job


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
        job.failure_reason = None

        saved_job = (
            self.job_repository.save(
                job
            )
        )

        job_monitor_payload = (
            build_job_monitor_payload(
                saved_job
            )
        )
        print(
            "JOB COMPLETE MONITOR PAYLOAD =",
            job_monitor_payload
        )

        emit_event(
            event_name=
                "JOB_COMPLETED",

            source=
                "WORKFLOW_ENGINE",

            status=
                "COMPLETED",

            **job_monitor_payload,
        )

        return saved_job


    def mark_failed(
        self,
        job: Job,
        error: str = "",
    ) -> Job:
        return self._mark_failed(
            job=job,
            error=error,
            failure_reason=JobFailureReason.ACTION_FAILED,
            expected_status=JobStatus.RUNNING,
        )

    def mark_dependency_failed(
        self,
        job: Job,
        error: str,
    ) -> Job:
        return self._mark_failed(
            job=job,
            error=error,
            failure_reason=JobFailureReason.DEPENDENCY_FAILED,
            expected_status=JobStatus.PENDING,
        )

    def _mark_failed(
        self,
        job: Job,
        error: str,
        failure_reason: JobFailureReason,
        expected_status: JobStatus,
    ) -> Job:

        if job.status != expected_status:
            raise ValueError(
                f"Chỉ Job {expected_status.value} mới được "
                "chuyển sang FAILED. "
                f"job_id={job.job_id}, "
                f"status={job.status}"
            )

        job.status = JobStatus.FAILED
        job.completed_at = datetime.now()
        job.result_message = None
        job.error_message = error
        job.failure_reason = failure_reason

        saved_job = (
            self.job_repository.save(
                job
            )
        )

        job_monitor_payload = (
            build_job_monitor_payload(
                saved_job
            )
        )

        emit_event(
            event_name=
                "JOB_FAILED",

            source=
                "WORKFLOW_ENGINE",

            status=
                "FAILED",

            error_message=
                saved_job.error_message,

            **job_monitor_payload,
        )

        return saved_job


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

    def _get_dependency_state(
        self,
        job: Job,
        jobs_in_request: List[Job],
    ) -> tuple[bool, str | None]:

        dependency_ids = (
            job.depends_on or []
        )

        if not dependency_ids:
            return True, None

        jobs_by_action_id = {
            item.action_id: item
            for item in jobs_in_request
        }
        failed_dependencies = []
        waiting_dependencies = []

        for dependency_action_id in (
            dependency_ids
        ):
            dependency_job = (
                jobs_by_action_id.get(
                    dependency_action_id
                )
            )

            if dependency_job is None:
                return False, (
                    "Dependency job không tồn tại: "
                    f"{dependency_action_id}"
                )

            if (
                dependency_job.status
                in {JobStatus.PENDING, JobStatus.RUNNING}
            ):
                waiting_dependencies.append(
                    dependency_action_id
                )
            elif dependency_job.status in {
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            }:
                failed_dependencies.append(
                    dependency_action_id
                )

        if waiting_dependencies:
            return False, None

        if failed_dependencies and not job.continue_on_error:
            return False, (
                "Dependency job thất bại: "
                + ", ".join(failed_dependencies)
            )

        return True, None

    @staticmethod
    def _dependency_cycles(
        jobs: List[Job],
    ) -> Dict[str, List[str]]:
        jobs_by_action_id = {
            job.action_id: job
            for job in jobs
        }
        visit_states: Dict[str, int] = {}
        action_stack: List[str] = []
        cycles: Dict[str, List[str]] = {}

        def visit(action_id: str) -> None:
            visit_states[action_id] = 1
            action_stack.append(action_id)

            for dependency_action_id in (
                jobs_by_action_id[action_id].depends_on
            ):
                if dependency_action_id not in jobs_by_action_id:
                    continue

                dependency_state = visit_states.get(
                    dependency_action_id,
                    0,
                )
                if dependency_state == 0:
                    visit(dependency_action_id)
                elif dependency_state == 1:
                    cycle_start = action_stack.index(
                        dependency_action_id
                    )
                    cycle = action_stack[cycle_start:]
                    for cycle_action_id in cycle:
                        cycles[cycle_action_id] = cycle

            action_stack.pop()
            visit_states[action_id] = 2

        for action_id in jobs_by_action_id:
            if visit_states.get(action_id, 0) == 0:
                visit(action_id)

        return cycles