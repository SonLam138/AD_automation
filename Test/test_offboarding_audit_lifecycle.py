import json
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.auto_engine.managers.active_execution_manager import (
    ActiveExecutionManager,
)
from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)
from app.auto_engine.models.job import Job, JobFailureReason, JobStatus
from app.auto_engine.workflow_engine.worker import Worker


class OffboardingAuditLifecycleTests(unittest.TestCase):
    def make_job(self, status, action_code="disable_user"):
        now = datetime.utcnow()
        return Job(
            job_id=f"REQ:{action_code}",
            request_id="REQ",
            workflow_id="OFFBOARDING_RESIGNED",
            action_id=action_code,
            action_code=action_code,
            display_name=action_code,
            execute_at=now,
            business_data={
                "source_request_id": "mail-42",
            },
            status=status,
            started_at=now,
            completed_at=now if status != JobStatus.RUNNING else None,
            failure_reason=(
                JobFailureReason.DEPENDENCY_FAILED
                if status == JobStatus.FAILED
                else None
            ),
            error_message=(
                "dependency failed"
                if status == JobStatus.FAILED
                else None
            ),
        )

    def test_worker_records_offboarding_action_result(self):
        job = self.make_job(JobStatus.RUNNING)
        job_manager = Mock()
        job_manager.claim_executable_jobs.return_value = [job]

        def mark_completed(job, message):
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()

        job_manager.mark_completed.side_effect = mark_completed

        class Action:
            def execute(self, **_kwargs):
                return {"success": True}

        class Registry:
            def get(self, _action_code):
                return Action()

        worker = Worker(job_manager, Registry())
        audit_record = SimpleNamespace(id=7)
        worker.offboarding_audit_repository = Mock()
        worker.offboarding_audit_repository.get_by_source_request_id.return_value = (
            audit_record
        )

        worker.update()

        worker.offboarding_audit_repository.record_step.assert_called_once()
        self.assertTrue(
            worker.offboarding_audit_repository.record_step.call_args.kwargs[
                "success"
            ]
        )

    def test_finalizer_records_dependency_failure_and_finishes_failed(self):
        jobs = [
            self.make_job(JobStatus.COMPLETED, "disable_user"),
            self.make_job(JobStatus.FAILED, "remove_all_groups"),
        ]
        execution = ActiveExecution(
            request_id="REQ",
            workflow_id="OFFBOARDING_RESIGNED",
            execute_at=datetime.utcnow(),
            actions=[],
            status=ActiveExecutionStatus.COMPLETED_WITH_ERRORS,
            business_data={
                "source_request_id": "mail-42",
                "target_object": {
                    "sam_account_name": "employee",
                },
            },
        )
        audit_record = SimpleNamespace(
            id=3,
            status="SCHEDULED",
            step_outcomes_json=json.dumps(
                [
                    {
                        "step": "disable_user",
                        "success": True,
                    }
                ]
            ),
        )
        manager = ActiveExecutionManager(
            active_execution_repository=Mock(),
            job_repository=Mock(),
        )
        manager.job_repository.list_by_request_id.return_value = jobs
        manager.offboarding_audit_repository = Mock()
        manager.offboarding_audit_repository.get_by_source_request_id.return_value = (
            audit_record
        )

        manager._finalize_offboarding_audit(execution)

        manager.offboarding_audit_repository.record_step.assert_called_once()
        failed_step = (
            manager.offboarding_audit_repository.record_step.call_args.kwargs
        )
        self.assertEqual(failed_step["step_name"], "remove_all_groups")
        self.assertFalse(failed_step["success"])
        manager.offboarding_audit_repository.finish.assert_called_once_with(
            audit_id=3,
            status="FAILED",
            actual_account="employee",
        )


if __name__ == "__main__":
    unittest.main()
