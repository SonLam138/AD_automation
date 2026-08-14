from app.auto_engine.workflow_engine.scheduler import (
    Scheduler,
)


class WorkflowEngine:

    def __init__(
        self,
        scheduler: Scheduler,
    ):
        self.scheduler = scheduler

    def tick(
        self,
    ) -> None:

        created_jobs = (
            self.scheduler.scan()
        )

        if created_jobs:

            print(
                "[WorkflowEngine] "
                f"Created {len(created_jobs)} job(s)"
            )