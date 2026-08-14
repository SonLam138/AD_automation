import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.auto_engine.models.job import (
    Job,
    JobStatus,
)


class JobRepository:

    def __init__(
        self,
        storage_path: str = "data/jobs",
    ):
        self.storage_path = Path(
            storage_path
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        job: Job,
    ) -> Job:
        job.updated_at = datetime.now()

        file_path = self._get_file_path(
            request_id=job.request_id,
            action_id=job.action_id,
        )

        temporary_file_path = (
            file_path.with_suffix(".tmp")
        )

        temporary_file_path.write_text(
            job.model_dump_json(
                indent=2,
            ),
            encoding="utf-8",
        )

        os.replace(
            temporary_file_path,
            file_path,
        )

        return job

    def get(
        self,
        request_id: str,
        action_id: str,
    ) -> Optional[Job]:
        file_path = self._get_file_path(
            request_id=request_id,
            action_id=action_id,
        )

        if not file_path.exists():
            return None

        return Job.model_validate_json(
            file_path.read_text(
                encoding="utf-8"
            )
        )

    def exists(
        self,
        request_id: str,
        action_id: str,
    ) -> bool:
        file_path = self._get_file_path(
            request_id=request_id,
            action_id=action_id,
        )

        return file_path.exists()

    def list_by_request_id(
        self,
        request_id: str,
    ) -> List[Job]:
        safe_request_id = self._safe_value(
            request_id
        )

        file_paths = sorted(
            self.storage_path.glob(
                f"{safe_request_id}__*.json"
            )
        )

        return [
            Job.model_validate_json(
                file_path.read_text(
                    encoding="utf-8"
                )
            )
            for file_path in file_paths
        ]

    def list_by_status(
        self,
        status: JobStatus,
    ) -> List[Job]:
        jobs: List[Job] = []

        for file_path in self.storage_path.glob(
            "*.json"
        ):
            job = Job.model_validate_json(
                file_path.read_text(
                    encoding="utf-8"
                )
            )

            if job.status == status:
                jobs.append(job)

        return jobs

    def delete(
        self,
        request_id: str,
        action_id: str,
    ) -> bool:
        file_path = self._get_file_path(
            request_id=request_id,
            action_id=action_id,
        )

        if not file_path.exists():
            return False

        file_path.unlink()

        return True

    def delete_by_request_id(
        self,
        request_id: str,
    ) -> int:
        safe_request_id = self._safe_value(
            request_id
        )

        deleted_count = 0

        for file_path in self.storage_path.glob(
            f"{safe_request_id}__*.json"
        ):
            file_path.unlink()

            deleted_count += 1

        return deleted_count

    def _get_file_path(
        self,
        request_id: str,
        action_id: str,
    ) -> Path:
        safe_request_id = self._safe_value(
            request_id
        )

        safe_action_id = self._safe_value(
            action_id
        )

        return self.storage_path / (
            f"{safe_request_id}"
            f"__"
            f"{safe_action_id}"
            f".json"
        )

    @staticmethod
    def _safe_value(
        value: str,
    ) -> str:
        return "".join(
            character
            if character.isalnum()
            or character in ("-", "_")
            else "_"
            for character in value
        )