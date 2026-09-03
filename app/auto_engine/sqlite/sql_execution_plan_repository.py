import json
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app.auto_engine.models.execution_plan import (
    ExecutionPlan,
)
from app.auto_engine.sqlite.db import SessionLocal
from app.auto_engine.sqlite.execution_plan_record import (
    ExecutionPlanRecord,
)


class SqlExecutionPlanRepository:

    def save(
        self,
        plan: ExecutionPlan,
    ) -> None:

        business_data = (
            plan.business_data
            or {}
        )

        target_object = (
            business_data.get(
                "target_object",
                {}
            )
            or {}
        )

        #
        # Custom Workflow:
        # target_object.business_data
        #
        # Temp Access:
        # target_object
        #
        # Offboarding:
        # target_object
        #
        object_data = (
            target_object.get(
                "business_data"
            )
            or target_object
        )

        target_object_type = (
            target_object.get(
                "object_type"
            )
        )

        if target_object_type:
            target_object_type = (
                target_object_type.upper()
            )

        target_account = (
            object_data.get(
                "sam_account_name"
            )
            or
            object_data.get(
                "group_name"
            )
            or
            object_data.get(
                "computer_name"
            )
        )

        session = SessionLocal()

        try:
            record = ExecutionPlanRecord(
                request_id=plan.request_id,
                workflow_id=plan.workflow_id,
                execute_at=plan.execute_at,

                target_object_type=
                    target_object_type,

                target_account=
                    target_account,

                execution_json=
                    plan.model_dump_json(),
            )

            session.add(record)
            session.commit()

        except IntegrityError as exc:
            session.rollback()

            raise ValueError(
                "ExecutionPlan đã tồn tại: "
                f"{plan.request_id}"
            ) from exc

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()

    def get(
        self,
        request_id: str,
    ) -> Optional[ExecutionPlan]:

        session = SessionLocal()

        try:
            record = session.get(
                ExecutionPlanRecord,
                request_id,
            )

            if record is None:
                return None

            data = json.loads(
                record.execution_json
            )

            return ExecutionPlan.model_validate(
                data
            )

        finally:
            session.close()