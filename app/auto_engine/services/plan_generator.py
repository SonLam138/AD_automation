from app.auto_engine.models.execution_plan import ExecutionPlan


class PlanGenerator:

    def generate(
        self,
        request,
        workflow
    ) -> ExecutionPlan:

        trigger_field = workflow.metadata.get("trigger_field")

        execute_at = request.business_data[trigger_field]

        return ExecutionPlan(
            request_id=request.request_id,
            workflow_id=workflow.workflow_id,
            execute_at=execute_at,
            actions=workflow.actions,
            business_data=request.business_data
        )