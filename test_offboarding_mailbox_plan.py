import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

from app.auto_engine.builders.active_execution_builder import (
    ActiveExecutionBuilder,
)
from app.auto_engine.models.request_models import (
    Request,
    RequestSource,
)
from app.auto_engine.models.request_type import (
    RequestType,
)
from app.auto_engine.models.source_types import (
    SourceType,
)
from app.auto_engine.resolver.object_resolver import (
    resolve_user,
)
from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver,
)
from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)
from app.auto_engine.services.job_repository import (
    JobRepository,
)
from app.auto_engine.services.plan_generator import (
    PlanGenerator,
)
from app.auto_engine.workflow_engine.scheduler import (
    Scheduler,
)


class OffboardingMailboxAdIntegrationTests(unittest.TestCase):

    def test_schedule_policy_stays_in_window_and_moves_late_request_to_next_day(self):
        generator = PlanGenerator()
        trigger_value = datetime(
            2026,
            9,
            1,
            0,
            0,
        )
        policy = {
            "start_hour": 17,
            "end_hour": 20,
        }

        with patch(
            "app.auto_engine.services.plan_generator.random.randint",
            return_value=90,
        ):
            execute_at = generator._get_scheduled_execute_at(
                trigger_value=trigger_value,
                schedule_policy=policy,
                now=datetime(
                    2026,
                    9,
                    1,
                    12,
                    0,
                ),
            )

        self.assertEqual(
            execute_at,
            datetime(
                2026,
                9,
                1,
                18,
                30,
            ),
        )

        with patch(
            "app.auto_engine.services.plan_generator.random.randint",
            return_value=0,
        ):
            late_execute_at = (
                generator._get_scheduled_execute_at(
                    trigger_value=trigger_value,
                    schedule_policy=policy,
                    now=datetime(
                        2026,
                        9,
                        1,
                        20,
                        0,
                        1,
                    ),
                )
            )

        self.assertEqual(
            late_execute_at,
            datetime(
                2026,
                9,
                2,
                17,
                0,
            ),
        )

    def test_ad_auto2_creates_jobs_from_offboarding_registry(self):
        target_object = resolve_user(
            {
                "email": "ad.auto2@automate.com.vn",
            }
        )

        self.assertEqual(
            target_object["sam_account_name"].lower(),
            "ad.auto2",
        )

        request = Request(
            request_id="REQ_AD_AUTO2_MAILBOX_TEST",
            request_type=RequestType.EMPLOYEE_OFFBOARDING,
            context="RESIGNED",
            source=RequestSource(
                source_type=SourceType.API
            ),
            business_data={
                "employee_id": "",
                "email": target_object["email"],
                "reason": "nghỉ việc",
                "start_date": datetime.now(),
                "target_object": target_object,
            },
        )

        workflow = WorkflowResolver().resolve(request)
        plan = PlanGenerator().generate(
            request=request,
            workflow=workflow,
        )
        active_execution = ActiveExecutionBuilder().build(plan)
        self.assertEqual(
            active_execution.execute_at,
            plan.execute_at,
        )

        with tempfile.TemporaryDirectory(
            prefix="offboarding-mailbox-test-"
        ) as storage_path:
            active_repository = ActiveExecutionRepository(
                storage_path=f"{storage_path}\\active_executions"
            )
            job_repository = JobRepository(
                storage_path=f"{storage_path}\\jobs"
            )
            scheduler = Scheduler(
                active_execution_repository=active_repository,
                job_repository=job_repository,
            )

            active_repository.save(active_execution)
            created_jobs = scheduler.scan()

            jobs = job_repository.list_by_request_id(
                request.request_id
            )

        self.assertEqual(
            len(created_jobs),
            len(plan.actions),
        )
        self.assertEqual(
            len(jobs),
            len(plan.actions),
        )
        self.assertEqual(
            {job.action_id for job in jobs},
            {action.id for action in plan.actions},
        )
        self.assertEqual(
            {job.action_code for job in jobs},
            {action.action_code for action in plan.actions},
        )
        self.assertTrue(
            all(
                job.execute_at >= plan.execute_at
                for job in jobs
            )
        )

        mailbox_jobs = [
            job
            for job in jobs
            if job.action_code == "onprem_disable_mailbox"
        ]

        if target_object["is_remote_mailbox"]:
            self.assertEqual(mailbox_jobs, [])
        else:
            self.assertEqual(len(mailbox_jobs), 1)
            self.assertEqual(
                mailbox_jobs[0].depends_on,
                ["STEP_01"],
            )
            self.assertEqual(
                mailbox_jobs[0].business_data[
                    "action_data"
                ]["STEP_MAILBOX"]["identity"],
                "ad.auto2",
            )


if __name__ == "__main__":
    unittest.main()
