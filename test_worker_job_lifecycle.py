import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from app.auto_engine.managers.active_execution_manager import (
    ActiveExecutionManager,
)
from app.auto_engine.managers.job_manager import (
    JobManager,
)
from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)
from app.auto_engine.models.job import (
    Job,
    JobFailureReason,
    JobStatus,
)
from app.auto_engine.models.workflow_definition import (
    WorkflowAction,
    WorkflowExecution,
)
from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)
from app.auto_engine.services.job_repository import (
    JobRepository,
)
from app.auto_engine.workflow_engine.worker import (
    Worker,
)


class WorkerJobLifecycleTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.job_repository = JobRepository(
            storage_path=str(root / "jobs")
        )
        self.active_execution_repository = (
            ActiveExecutionRepository(
                storage_path=str(root / "active_executions")
            )
        )
        self.job_manager = JobManager(
            self.job_repository
        )
        self.emit_event_patch = patch(
            "app.auto_engine.managers.job_manager.emit_event"
        )
        self.emit_event = self.emit_event_patch.start()
        self.addCleanup(self.emit_event_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

    @staticmethod
    def make_job(
        action_id,
        depends_on=None,
        continue_on_error=False,
        execute_at=None,
    ):
        return Job(
            job_id=f"REQ:{action_id}",
            request_id="REQ",
            workflow_id="WF",
            action_id=action_id,
            action_code=action_id,
            display_name=action_id,
            execute_at=execute_at or (
                datetime.now() - timedelta(seconds=1)
            ),
            depends_on=depends_on or [],
            continue_on_error=continue_on_error,
            max_retry=3,
        )

    def make_active_execution(self, actions):
        execution = ActiveExecution(
            request_id="REQ",
            workflow_id="WF",
            execute_at=datetime.now(),
            actions=[
                WorkflowAction(
                    id=action_id,
                    action_code=action_id,
                    display_name=action_id,
                    execution=WorkflowExecution(
                        depends_on=depends_on or [],
                        continue_on_error=continue_on_error,
                    ),
                )
                for action_id, depends_on, continue_on_error
                in actions
            ],
            status=ActiveExecutionStatus.JOB_CREATED,
        )
        self.active_execution_repository.save(execution)
        return execution

    def fail_running_job(self, job):
        self.job_manager.mark_running(job)
        return self.job_manager.mark_failed(
            job,
            "action execution failed",
        )

    def active_execution_manager(self):
        return ActiveExecutionManager(
            active_execution_repository=(
                self.active_execution_repository
            ),
            job_repository=self.job_repository,
        )

    def test_worker_failure_is_final_without_job_retry(self):
        action_results = (
            {"success": False, "error": "returned failure"},
            RuntimeError("raised failure"),
        )
        for index, action_result in enumerate(action_results):
            with self.subTest(action_result=action_result):
                job = self.make_job(f"ACTION_{index}")
                self.job_repository.save(job)
                self.emit_event.reset_mock()

                class Action:
                    def execute(_self, **_kwargs):
                        if isinstance(action_result, Exception):
                            raise action_result
                        return action_result

                class Registry:
                    def get(_self, _action_code):
                        return Action()

                Worker(
                    self.job_manager,
                    Registry(),
                ).update()

                saved_job = self.job_repository.get(
                    job.request_id,
                    job.action_id,
                )
                self.assertEqual(
                    saved_job.status,
                    JobStatus.FAILED,
                )
                self.assertEqual(saved_job.retry_count, 0)
                self.assertEqual(
                    saved_job.failure_reason,
                    JobFailureReason.ACTION_FAILED,
                )
                self.assertEqual(
                    [call.kwargs["event_name"]
                     for call in self.emit_event.call_args_list],
                    ["JOB_STARTED", "JOB_FAILED"],
                )

    def test_dependency_failure_without_continue_fails_instead_of_pending(self):
        self.make_active_execution([
            ("SOURCE", [], False),
            ("BLOCKED", ["SOURCE"], False),
        ])
        source = self.make_job("SOURCE")
        blocked = self.make_job(
            "BLOCKED",
            depends_on=["SOURCE"],
        )
        self.job_repository.save(source)
        self.job_repository.save(blocked)
        self.fail_running_job(source)

        claimed = self.job_manager.claim_executable_jobs()
        saved_blocked = self.job_repository.get(
            "REQ",
            "BLOCKED",
        )

        self.assertEqual(claimed, [])
        self.assertEqual(saved_blocked.status, JobStatus.FAILED)
        self.assertEqual(
            saved_blocked.failure_reason,
            JobFailureReason.DEPENDENCY_FAILED,
        )
        self.assertIsNotNone(saved_blocked.completed_at)
        failed_event = next(
            call.kwargs
            for call in self.emit_event.call_args_list
            if call.kwargs["event_name"] == "JOB_FAILED"
            and call.kwargs["job_id"] == saved_blocked.job_id
        )
        self.assertEqual(
            failed_event["failure_reason"],
            JobFailureReason.DEPENDENCY_FAILED.value,
        )

    def test_pending_dependency_keeps_dependent_job_waiting(self):
        source = self.make_job("SOURCE")
        dependent = self.make_job(
            "DEPENDENT",
            depends_on=["SOURCE"],
        )
        self.job_repository.save(source)
        self.job_repository.save(dependent)

        claimed = self.job_manager.claim_executable_jobs()
        saved_dependent = self.job_repository.get(
            "REQ",
            "DEPENDENT",
        )

        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0].action_id, "SOURCE")
        self.assertEqual(
            saved_dependent.status,
            JobStatus.PENDING,
        )
        self.assertIsNone(saved_dependent.failure_reason)

    def test_successful_execution_still_completes_active_execution(self):
        self.make_active_execution([
            ("ONLY_ACTION", [], False),
        ])
        job = self.make_job("ONLY_ACTION")
        self.job_repository.save(job)

        claimed = self.job_manager.claim_executable_jobs()
        self.assertEqual(len(claimed), 1)
        self.job_manager.mark_completed(
            claimed[0],
            "action succeeded",
        )

        active = self.active_execution_repository.get("REQ")
        self.active_execution_manager()._update_execution(active)
        self.assertEqual(
            active.status,
            ActiveExecutionStatus.COMPLETED,
        )

    def test_successful_continue_after_dependency_failure_completes_with_errors(self):
        self.make_active_execution([
            ("SOURCE", [], False),
            ("CONTINUED", ["SOURCE"], True),
        ])
        source = self.make_job("SOURCE")
        continued = self.make_job(
            "CONTINUED",
            depends_on=["SOURCE"],
            continue_on_error=True,
        )
        self.job_repository.save(source)
        self.job_repository.save(continued)
        self.fail_running_job(source)

        self.active_execution_manager().update()
        active = self.active_execution_repository.get("REQ")
        self.assertEqual(
            active.status,
            ActiveExecutionStatus.JOB_CREATED,
        )

        claimed = self.job_manager.claim_executable_jobs()
        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0].action_id, "CONTINUED")
        self.assertEqual(claimed[0].status, JobStatus.RUNNING)

        self.job_manager.mark_completed(
            claimed[0],
            "continued action succeeded",
        )
        self.active_execution_manager().update()
        active = self.active_execution_repository.get("REQ")
        self.assertIsNotNone(active)
        self.assertEqual(
            active.status,
            ActiveExecutionStatus.COMPLETED_WITH_ERRORS,
        )
        self.assertFalse(
            self.active_execution_repository.list_active()
        )
        self.assertEqual(
            self.job_repository.get("REQ", "SOURCE").status,
            JobStatus.FAILED,
        )

    def test_continued_action_failure_is_real_execution_failure(self):
        self.make_active_execution([
            ("SOURCE", [], False),
            ("CONTINUED", ["SOURCE"], True),
        ])
        source = self.make_job("SOURCE")
        continued = self.make_job(
            "CONTINUED",
            depends_on=["SOURCE"],
            continue_on_error=True,
        )
        self.job_repository.save(source)
        self.job_repository.save(continued)
        self.fail_running_job(source)

        claimed = self.job_manager.claim_executable_jobs()
        self.assertEqual(len(claimed), 1)
        self.job_manager.mark_failed(
            claimed[0],
            "continued action failed itself",
        )

        active = self.active_execution_repository.get("REQ")
        self.active_execution_manager()._update_execution(active)
        self.assertEqual(
            active.status,
            ActiveExecutionStatus.FAILED,
        )

    def test_missing_dependency_fails_job(self):
        job = self.make_job(
            "ORPHAN",
            depends_on=["MISSING"],
        )
        self.job_repository.save(job)

        self.job_manager.claim_executable_jobs()
        saved_job = self.job_repository.get(
            "REQ",
            "ORPHAN",
        )

        self.assertEqual(saved_job.status, JobStatus.FAILED)
        self.assertEqual(
            saved_job.failure_reason,
            JobFailureReason.DEPENDENCY_FAILED,
        )

    def test_dependency_cycle_fails_instead_of_remaining_pending(self):
        first = self.make_job(
            "FIRST",
            depends_on=["SECOND"],
            execute_at=datetime.now() + timedelta(days=1),
        )
        second = self.make_job(
            "SECOND",
            depends_on=["FIRST"],
            execute_at=datetime.now() + timedelta(days=1),
        )
        self.job_repository.save(first)
        self.job_repository.save(second)

        self.job_manager.claim_executable_jobs()

        for action_id in ("FIRST", "SECOND"):
            saved_job = self.job_repository.get(
                "REQ",
                action_id,
            )
            self.assertEqual(saved_job.status, JobStatus.FAILED)
            self.assertEqual(
                saved_job.failure_reason,
                JobFailureReason.DEPENDENCY_FAILED,
            )


if __name__ == "__main__":
    unittest.main()
