from datetime import datetime
import uuid

from app.auto_engine.models.request_models import Request
from app.auto_engine.models.execution_plan import ExecutionPlan

from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver
)

from app.auto_engine.services.plan_generator import (
    PlanGenerator
)

from app.auto_engine.services.execution_plan_repository import (
    ExecutionPlanRepository
)


class WorkflowPlanEngine:

    def __init__(
        self,
        workflow_resolver: WorkflowResolver,
        plan_generator: PlanGenerator,
        plan_repository: ExecutionPlanRepository
    ):
        self.workflow_resolver = workflow_resolver
        self.plan_generator = plan_generator
        self.plan_repository = plan_repository

    def _generate_request_id(
        self
    ) -> str:

        date_part = datetime.now().strftime(
            "%d%m%Y"
        )

        random_part = (
            uuid.uuid4()
            .hex[:4]
            .upper()
        )

        return (
            f"REQ_{date_part}_{random_part}"
        )

    def process(
        self,
        request: Request
    ) -> ExecutionPlan:

        if request.request_id is None:

            request.request_id = (
                self._generate_request_id()
            )

        workflow = (
            self.workflow_resolver.resolve(
                request
            )
        )

        plan = (
            self.plan_generator.generate(
                request=request,
                workflow=workflow
            )
        )

        self.plan_repository.save(
            plan
        )

        return plan