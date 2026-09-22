import json
from datetime import datetime

from app.auto_engine.models.request_models import (
    Request,
)

from app.auto_engine.sqlite.access_snapshot import (
    AccessSnapshot,
)

from app.auto_engine.sqlite.access_snapshot_repository import (
    AccessSnapshotRepository,
)


class AccessSnapshotService:

    def __init__(
        self,
        repository: AccessSnapshotRepository,
    ):
        self.repository = repository

    def save_snapshot(
        self,
        request: Request,
    ) -> None:

        if not request.snapshot_data:
            return

        snapshot_data = (
            request.snapshot_data
        )

        snapshot = AccessSnapshot(

            request_id=
                request.request_id,

            request_context=
                snapshot_data[
                    "request_context"
                ],

            employee_id=
                snapshot_data[
                    "employee_id"
                ],

            sam_account_name=
                snapshot_data[
                    "sam_account_name"
                ],

            captured_at=
                datetime.now(),

            snapshot_json=
                json.dumps(
                    snapshot_data[
                        "snapshot_json"
                    ],
                    ensure_ascii=False,
                ),
        )

        self.repository.save(
            snapshot
        )

    def get_by_request_id(
        self,
        request_id: str,
    ):

        return (
            self.repository
            .get_by_request_id(
                request_id
            )
        )

    def get_latest_by_sam_account_name(
        self,
        sam_account_name: str,
    ):

        return (
            self.repository
            .get_latest_by_sam_account_name(
                sam_account_name
            )
        )

    def get_latest_by_employee_id(
        self,
        employee_id: str,
    ):

        return (
            self.repository
            .get_latest_by_employee_id(
                employee_id
            )
        )