from datetime import datetime
import json

from app.auto_engine.sqlite.access_snapshot import (
    AccessSnapshot,
)

from app.auto_engine.sqlite.access_snapshot_repository import (
    AccessSnapshotRepository,
)


def main():

    repo = (
        AccessSnapshotRepository()
    )

    snapshot = AccessSnapshot(

        request_id=
            "REQ_TEST_001",

        request_context=
            "OFFBOARDING",

        employee_id=
            "E00001",

        sam_account_name=
            "test.user",

        captured_at=
            datetime.now(),

        snapshot_json=
            json.dumps({
                "ou_dn":
                    "OU=Trading",

                "groups": [
                    "GG_VPN",
                    "GG_SHAREPOINT",
                ]
            })
    )

    repo.save(
        snapshot
    )

    print(
        repo.get_by_request_id(
            "REQ_TEST_001"
        )
    )

    print(
        repo.get_latest_by_sam_account_name(
            "test.user"
        )
    )


if __name__ == "__main__":
    main()