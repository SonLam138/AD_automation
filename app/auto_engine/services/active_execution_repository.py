import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.auto_engine.models.active_execution import (
    ActiveExecution,
    ActiveExecutionStatus,
)


class ActiveExecutionRepository:

    def __init__(
        self,
        storage_path: str = "data/active_executions",
    ):
        self.storage_path = Path(storage_path)

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _get_file_path(
        self,
        request_id: str,
    ) -> Path:
        return (
            self.storage_path
            / f"{request_id}.json"
        )

    def save(
        self,
        active_execution: ActiveExecution,
    ) -> None:
        active_execution.updated_at = datetime.now()

        file_path = self._get_file_path(
            active_execution.request_id
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                active_execution.model_dump(
                    mode="json"
                ),
                f,
                indent=2,
                ensure_ascii=False,
            )

    def get(
        self,
        request_id: str,
    ) -> Optional[ActiveExecution]:
        file_path = self._get_file_path(
            request_id
        )

        if not file_path.exists():
            return None

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        return ActiveExecution.model_validate(data)

    def list_active(self) -> List[ActiveExecution]:
        active_executions: List[ActiveExecution] = []

        for file_path in self.storage_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            active_execution = ActiveExecution.model_validate(data)

            if active_execution.status not in {
                ActiveExecutionStatus.COMPLETED,
                ActiveExecutionStatus.CANCELLED,
            }:
                active_executions.append(active_execution)

        return active_executions

    def delete(
        self,
        request_id: str,
    ) -> bool:
        file_path = self._get_file_path(
            request_id
        )

        if not file_path.exists():
            return False

        file_path.unlink()

        return True