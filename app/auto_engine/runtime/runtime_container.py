from app.auto_engine.resolver.workflow_resolver import (
    WorkflowResolver,
)

from app.auto_engine.services.plan_generator import (
    PlanGenerator,
)

from app.auto_engine.resolver.workflow_plan_engine import (
    WorkflowPlanEngine,
)

from app.auto_engine.services.execution_plan_repository import (
    ExecutionPlanRepository,
)

from app.auto_engine.services.active_execution_repository import (
    ActiveExecutionRepository,
)

from app.auto_engine.services.job_repository import (
    JobRepository,
)

from app.auto_engine.workflow_engine.scheduler import (
    Scheduler,
)

from app.auto_engine.workflow_engine.workflow_engine import (
    WorkflowEngine,
)

from app.auto_engine.runtime.workflow_runtime import (
    WorkflowRuntime,
)

from app.auto_engine.managers.active_execution_manager import (
    ActiveExecutionManager,
)

from app.auto_engine.managers.job_manager import (
    JobManager,
)
from app.auto_engine.actions.ad_actions import *
from app.auto_engine.workflow_engine.worker import (
Worker,
)
# ==================================================
# REPOSITORIES
# ==================================================

execution_plan_repository = (
    ExecutionPlanRepository()
)

active_execution_repository = (
    ActiveExecutionRepository()
)

job_repository = (
    JobRepository()
)


# ==================================================
# PLAN ENGINE
#
# Normalized Request
#     ↓
# ExecutionPlan
# ==================================================

workflow_plan_engine = WorkflowPlanEngine(
    workflow_resolver=WorkflowResolver(),

    plan_generator=PlanGenerator(),

    plan_repository=(
        execution_plan_repository
    ),
)


# ==================================================
# SCHEDULER
#
# ActiveExecution
#     ↓
# Job
# ==================================================

scheduler = Scheduler(
    active_execution_repository=(
        active_execution_repository
    ),

    job_repository=(
        job_repository
    ),
)
# ==================================================
# MANAGER
# ==================================================
active_execution_manager = (
    ActiveExecutionManager(
        active_execution_repository=(
            active_execution_repository
        ),
        job_repository=job_repository,
    )
)

job_manager = JobManager(
    job_repository=job_repository,
)


# ==================================================
# WORKFLOW ENGINE
#
# Scheduler
# Sau này nối thêm Worker tại đây.
# ==================================================

workflow_engine = WorkflowEngine(
    scheduler=scheduler,
)


# ==================================================
# RUNTIME TỔNG
#
# run_plan_engine()
#     Adapter → Plan → Active
#
# start_workflow_engine()
#     Scheduler scan liên tục
# ==================================================

# REGISTRY ACTION FOR WOKER - MAPING WITH AD_ACTION.PY

action_registry = (
    AdActionRegistry()
)

# ==================================================
# USER ACTIONS
# ==================================================
action_registry.register(
    "disable_user",
    DisableUserAction(),
)

action_registry.register(
    "enable_user",
    EnableUserAction(),
)

action_registry.register(
    "add_group",
    AddGroupAction(),
)

action_registry.register(
    "remove_group",
    RemoveGroupAction(),
)

action_registry.register(
    "move_user_to_ou",
    MoveUserToOuAction(),
)

action_registry.register(
    "remove_all_groups",
    RemoveAllGroupsAction(),
    )
# ==================================================
# COMPUTER ACTIONS
# ==================================================

action_registry.register(
    "disable_computer",
    DisableComputerAction(),
)

action_registry.register(
    "move_computer_to_ou",
    MoveComputerToOuAction(),
)

# ==================================================
# GROUP ACTIONS
# ==================================================

action_registry.register(
    "move_group_to_ou",
    MoveGroupToOuAction(),
)




worker = Worker(
    job_manager=job_manager,
    action_registry=(
    action_registry
    ),
)

workflow_runtime = WorkflowRuntime(
    workflow_plan_engine=(
        workflow_plan_engine
    ),

    workflow_engine=(
        workflow_engine
    ),

    active_execution_repository=(
        active_execution_repository
    ),
    active_execution_manager=(active_execution_manager),
    job_manager=(job_manager),

    worker=worker,

    scan_interval_seconds=10,
)

