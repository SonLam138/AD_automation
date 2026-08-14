from copy import deepcopy
from datetime import timedelta
from typing import List

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


class Scheduler:

    def __init__(
        self,
        active_execution_repository:
            ActiveExecutionRepository,
        job_repository:
            JobRepository,
    ):
        self.active_execution_repository = (
            active_execution_repository
        )

        self.job_repository = (
            job_repository
        )

    def scan(
        self,
    ) -> List[Job]:
        created_jobs: List[Job] = []

        active_executions = (
            self.active_execution_repository.list_active()
        )
        print(
        f"[Scheduler] Active executions: "
        f"{len(active_executions)}"
        )
        for active_execution in active_executions:

            print(
            active_execution.request_id,
            len(active_execution.actions)
            )
            if (
                active_execution.status
                != ActiveExecutionStatus.SCHEDULED
            ):
                continue

            jobs = self._create_jobs(
                active_execution
            )

            created_jobs.extend(
                jobs
            )

            persisted_jobs = (
                self.job_repository.list_by_request_id(
                    active_execution.request_id
                )
            )

            expected_action_ids = {
                action.id
                for action in active_execution.actions
            }

            persisted_action_ids = {
                job.action_id
                for job in persisted_jobs
            }

            if (
                persisted_action_ids
                != expected_action_ids
            ):
                continue

            active_execution.status = (
                ActiveExecutionStatus.JOB_CREATED
            )

            self.active_execution_repository.save(
                active_execution
            )

        return created_jobs

    def _create_jobs(
        self,
        active_execution: ActiveExecution,
    ) -> List[Job]:
        created_jobs: List[Job] = []

        for action in active_execution.actions:
            existing_job = self.job_repository.get(
                request_id=active_execution.request_id,
                action_id=action.id,
            )

            if existing_job is not None:
                continue

            job = self._build_job(
                active_execution=active_execution,
                action=action,
            )

            self.job_repository.save(
                job
            )

            created_jobs.append(
                job
            )

        return created_jobs

    def _build_job(
        self,
        active_execution: ActiveExecution,
        action,
    ) -> Job:
        job_execute_at = (
            active_execution.execute_at
            + timedelta(
                minutes=(
                    action.execution.delay_minutes
                )
            )
        )

        job_id = (
            f"{active_execution.request_id}"
            f":"
            f"{action.id}"
        )

        return Job(
            job_id=job_id,

            request_id=(
                active_execution.request_id
            ),

            workflow_id=(
                active_execution.workflow_id
            ),

            action_id=action.id,

            action_code=action.action_code,

            display_name=action.display_name,

            execute_at=job_execute_at,

            depends_on=list(
                action.execution.depends_on
            ),

            max_retry=(
                action.execution.retry_count
            ),

            continue_on_error=(
                action.execution.continue_on_error
            ),

            business_data=deepcopy(
                active_execution.business_data
            ),

            status=JobStatus.PENDING,
        )