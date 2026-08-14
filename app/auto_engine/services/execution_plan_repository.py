import json
from pathlib import Path
from typing import Optional

from app.auto_engine.models.execution_plan import ExecutionPlan


class ExecutionPlanRepository:
    def __init__(
        self,
        storage_path: str = "data/execution_plans"
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def save(self, plan: ExecutionPlan):
        file_path = self.storage_path / f"{plan.request_id}.json"
        print("SAVE PATH:", file_path)

        print("ABS PATH :", file_path.resolve())
        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                plan.model_dump(mode="json"),
                f,
                indent=2,
                ensure_ascii=False
            )

    def get(
        self,
        request_id: str
    ) -> Optional[ExecutionPlan]:

        file_path = self.storage_path / f"{request_id}.json"
        print("LOAD ABS :", file_path.resolve())
        print("EXISTS :", file_path.exists())

        if not file_path.exists():
            return None

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        return ExecutionPlan.model_validate(data)