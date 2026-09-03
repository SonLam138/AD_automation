import json
from pathlib import Path
from datetime import datetime
import uuid
from app.auto_engine.sqlite.workflow_journal_storage import (
    SqlWorkflowJournalStorage
)

class WorkflowJournalRepository:

    def __init__(self):

        self.file_path = (
            Path(__file__).parent.parent.parent.parent
            / "data"
            /"workflow_ui"
            / "workflow_ui_journal.json"
        )
        self.storage = (
            SqlWorkflowJournalStorage()
        )

    # def _load(self):

    #     with open(
    #         self.file_path,
    #         "r",
    #         encoding="utf-8"
    #     ) as f:

    #         return json.load(f)
    def _load(self):

        return {
            "entries":
                self.storage.list_entries()
        }

    def _save_file(
        self,
        data,
    ):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    def save(
        self,
        *,
        workflow_name: str,
        created_by: str,
        snapshot: dict,
    ):

        entry = {
            "journal_id": (
                f"JRN_{uuid.uuid4().hex[:8]}"
            ),

            "workflow_name": workflow_name,

            "workflow_id":
                snapshot["workflowInfo"][
                    "workflowId"
                ],

            "created_by": created_by,

            "status": "saved",

            "executed_at": None,

            "saved_at": (
                datetime.now()
            ),

            "object_count": len(
                snapshot.get(
                    "objects",
                    []
                )
            ),

            "step_count": len(
                snapshot.get(
                    "steps",
                    []
                )
            ),

            "snapshot": snapshot,
        }

        self.storage.save_entry(
            entry
        )

        return entry

    def list_by_user(
        self,
        username: str,
    ):

        data = self._load()

        result = []

        for entry in data.get(
            "entries",
            []
        ):

            if (
                entry.get("created_by")
                != username
            ):
                continue

            result.append(
                {
                    "journal_id":
                        entry.get(
                            "journal_id"
                        ),

                    "workflow_id":
                        entry.get(
                            "workflow_id"
                        ),

                    "workflow_name":
                        entry.get(
                            "workflow_name"
                        ),

                    "created_by":
                        entry.get(
                            "created_by"
                        ),

                    "saved_at":
                        entry.get(
                            "saved_at"
                        ),
                    "status": entry.get("status", "saved"),

                    "object_count": entry.get("object_count", 0),

                    "object_count":
                        entry.get(
                            "object_count",
                            0
                        ),

                    "step_count":
                        entry.get(
                            "step_count",
                            0
                        )
                }
            )

        return result

    def get_by_id(
        self,
        journal_id: str
    ):
        data = self._load()

        for entry in data["entries"]:
            if entry["journal_id"] == journal_id:
                return entry

        return None


    def delete(
        self,
        journal_id: str,
    ):

        return self.storage.delete_entry(
            journal_id
        )

    # --------------------------------------------------
    # Registry Cleanup
    #
    # Remove workflow template from workflow_registry.json
    # when deleting a saved workflow journal.
    #
    # NOTE:
    # Current implementation is colocated here to keep
    # delete workflow flow simple.
    # If registry management grows later, extract into
    # dedicated WorkflowRegistryRepository.
    # ---------------------------------------
    def delete_registry_workflow(
        self,
        workflow_id: str
    ):
        if not workflow_id:
            return False

        registry_path = (
            Path(__file__).parent.parent
            / "resolver"
            / "workflow_registry.json"
        )

        with open(
            registry_path,
            "r",
            encoding="utf-8"
        ) as f:

            templates = json.load(f)

        original_count = len(
            templates
        )

        templates = [
            template
            for template in templates
            if template.get("workflow_id")
            != workflow_id
        ]

        deleted = (
            len(templates)
            < original_count
        )

        if deleted:

            with open(
                registry_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    templates,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        return deleted

    def mark_executed(
        self,
        workflow_id: str,
    ):

        return self.storage.update_status(
            workflow_id=workflow_id,
            status="executed",
            executed_at=datetime.now(),
        )