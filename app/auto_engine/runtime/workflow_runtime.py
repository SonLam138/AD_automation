import threading
import time
from copy import deepcopy
from typing import Any, Dict

from app.auto_engine.models.base import (
    SourceAdapter,
)

from app.auto_engine.models.execution_plan import (
    ExecutionPlan,
)

from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)

from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)

from app.auto_engine.resolver.workflow_plan_engine import (
    WorkflowPlanEngine,
)

from app.auto_engine.workflow_engine.workflow_engine import (
    WorkflowEngine,
)
from app.auto_engine.managers.active_execution_manager import (
    ActiveExecutionManager,
)

from app.auto_engine.managers.job_manager import (
    JobManager,
)
from app.auto_engine.workflow_engine.worker import Worker
import traceback

class WorkflowRuntime:

    def __init__(
        self,
        workflow_plan_engine:
            WorkflowPlanEngine,

        workflow_engine:
            WorkflowEngine,

        active_execution_repository:
            ActiveExecutionRepository,

        active_execution_manager:
            ActiveExecutionManager,

        job_manager:
            JobManager,

        worker:Worker,

        scan_interval_seconds: int = 10,
    ):
        self.workflow_plan_engine = (
            workflow_plan_engine
        )

        self.workflow_engine = (
            workflow_engine
        )

        self.active_execution_repository = (
            active_execution_repository
        )

        self.scan_interval_seconds = (
            scan_interval_seconds
        )

        self.active_execution_manager = (
            active_execution_manager
        )

        self.job_manager = (
            job_manager
        )
        self.worker=worker

        self._workflow_engine_running = False

        self._workflow_engine_thread: (
            threading.Thread | None
        ) = None

    # ==================================================
    # PHASE 1
    # Adapter
    #     ↓
    # Normalized Request
    #     ↓
    # WorkflowPlanEngine
    #     ↓
    # ExecutionPlan
    #     ↓
    # ActiveExecution
    #
    # Hàm này chỉ chạy khi có input mới.
    # Không nằm trong vòng scan 10 giây.
    # ==================================================

    def run_plan_engine(
        self,
        adapter: SourceAdapter,
        source_data: Dict[str, Any],
    ) -> ExecutionPlan:

        normalized_request = adapter.parse(
            source_data
        )

        plan = (
            self.workflow_plan_engine.process(
                normalized_request
            )
        )

        self.plan_to_active(
            plan
        )

        return plan

    # ==================================================
    # BRIDGE GIỮA HAI ENGINE
    #
    # ExecutionPlan
    #     ↓
    # ActiveExecution
    #
    # Chỉ xử lý đúng plan vừa được tạo.
    # Không list_all ExecutionPlanRepository.
    # ==================================================

    def plan_to_active(
        self,
        plan: ExecutionPlan,
    ) -> ActiveExecution:

        existing_active = (
            self.active_execution_repository.get(
                plan.request_id
            )
        )

        if existing_active is not None:

            return existing_active

        active_execution = ActiveExecution(
            request_id=plan.request_id,

            workflow_id=plan.workflow_id,

            execute_at=plan.execute_at,

            actions=deepcopy(
                plan.actions
            ),

            business_data=deepcopy(
                plan.business_data
            ),

            status=(
                ActiveExecutionStatus.SCHEDULED
            ),
        )

        self.active_execution_repository.save(
            active_execution
        )

        return active_execution

    # ==================================================
    # PHASE 2
    # Workflow Engine chạy nền liên tục.
    #
    # Hiện tại tick() sẽ gọi Scheduler.
    # Sau khi nối Worker thì tick() gọi tiếp Worker.
    # ==================================================

    def start_workflow_engine(
        self,
    ) -> None:
        print("START WORKFLOW ENGINE")
        if self._workflow_engine_running:
            return

        self._workflow_engine_running = True

        self._workflow_engine_thread = (
            threading.Thread(
                target=(
                    self._workflow_engine_loop
                ),

                name="workflow-engine-runtime",

                daemon=True,
            )
        )

        self._workflow_engine_thread.start()

        print(
            "[WorkflowRuntime] "
            "Workflow Engine started"
        )

    def stop_workflow_engine(
        self,
    ) -> None:

        self._workflow_engine_running = False

        if (
            self._workflow_engine_thread
            is not None
            and
            self._workflow_engine_thread
            .is_alive()
        ):
            self._workflow_engine_thread.join(
                timeout=(
                    self.scan_interval_seconds
                    + 1
                )
            )

        print(
            "[WorkflowRuntime] "
            "Workflow Engine stopped"
        )

    def run_workflow_engine_cycle(
        self,
    ) -> None:

        print(
            "[Runtime] ActiveExecutionManager"
        )
        self.active_execution_manager.update()

        print(
            "[Runtime] Workflow Engine"
        )
        self.workflow_engine.tick()

        print(
            "[Runtime] JobManager"
        )
        self.job_manager.update()

        print(
            "[Runtime] "
            "Worker"
        )
        self.worker.update()

    def _workflow_engine_loop(
        self,
    ) -> None:

        while self._workflow_engine_running:
            print("RUNTIME LOOP")
            try:

                self.run_workflow_engine_cycle()

            except Exception as ex:

                print(
                    "[WorkflowRuntime] "
                    "Workflow Engine cycle failed: "
                    #f"{ex}"
                )
                traceback.print_exc()

            time.sleep(
                self.scan_interval_seconds
            )