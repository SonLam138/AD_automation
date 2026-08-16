import json
import os

from pathlib import Path
from typing import (
    Any,
    Dict,
    Optional,
)


# ==================================================
# STORAGE PATH
# ==================================================

REVIEW_SESSION_DIR = Path(
    "data/bulk_request_reviews"
)


# ==================================================
# REVIEW SESSION REPOSITORY
# ==================================================

class ReviewSessionRepository:

    def __init__(
        self,
        storage_dir: Path = REVIEW_SESSION_DIR,
    ):

        self.storage_dir = (
            storage_dir
        )

        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )


    # ==============================================
    # BUILD FILE PATH
    # ==============================================

    def _get_file_path(
        self,
        session_id: str,
    ) -> Path:

        if not session_id:

            raise ValueError(
                "Missing review session ID"
            )

        
        safe_session_id = (
            session_id
            .replace("/", "")
            .replace("\\", "")
            .replace("..", "")
        )

        if (
            safe_session_id
            != session_id
        ):

            raise ValueError(
                "Invalid review session ID"
            )

        return (
            self.storage_dir
            /
            f"{safe_session_id}.json"
        )


    # ==============================================
    # SAVE SESSION
    # ==============================================

    def save(
        self,
        session: Dict[str, Any],
    ) -> None:

        session_id = session.get(
            "session_id"
        )

        if not session_id:

            raise ValueError(
                "Review session requires session_id"
            )

        file_path = (
            self._get_file_path(
                session_id
            )
        )

        temp_file_path = (
            file_path.with_suffix(
                ".json.tmp"
            )
        )

        with temp_file_path.open(
            mode="w",
            encoding="utf-8",
        ) as file_handle:

            json.dump(
                session,
                file_handle,
                ensure_ascii=False,
                indent=2,
            )

            file_handle.flush()

            os.fsync(
                file_handle.fileno()
            )

        os.replace(
            temp_file_path,
            file_path,
        )


    # ==============================================
    # GET SESSION
    # ==============================================

    def get(
        self,
        session_id: str,
    ) -> Optional[
        Dict[str, Any]
    ]:

        file_path = (
            self._get_file_path(
                session_id
            )
        )

        if not file_path.exists():

            return None

        with file_path.open(
            mode="r",
            encoding="utf-8",
        ) as file_handle:

            return json.load(
                file_handle
            )


    # ==============================================
    # EXISTS
    # ==============================================

    def exists(
        self,
        session_id: str,
    ) -> bool:

        return (
            self._get_file_path(
                session_id
            )
            .exists()
        )


    # ==============================================
    # DELETE SESSION
    # ==============================================

    def delete(
        self,
        session_id: str,
    ) -> bool:

        file_path = (
            self._get_file_path(
                session_id
            )
        )

        if not file_path.exists():

            return False

        file_path.unlink()

        return True