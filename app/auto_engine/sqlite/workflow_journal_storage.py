import json

from app.auto_engine.sqlite.db import (
    SessionLocal,
)
from app.auto_engine.sqlite.workflow_journal_record import (
    WorkflowJournalRecord,
)
from datetime import datetime

class SqlWorkflowJournalStorage:

    def save_entry(
        self,
        entry: dict,
    ):

        session = SessionLocal()

        try:

            record = WorkflowJournalRecord(
                journal_id=entry["journal_id"],
                workflow_id=entry["workflow_id"],
                workflow_name=entry["workflow_name"],
                created_by=entry["created_by"],
                status=entry["status"],
                saved_at=entry["saved_at"],
                executed_at=entry["executed_at"],
                object_count=entry["object_count"],
                step_count=entry["step_count"],
                snapshot_json=json.dumps(
                    entry["snapshot"],
                    ensure_ascii=False,
                ),
            )

            session.add(record)

            session.commit()

        finally:
            session.close()

    def list_entries(
        self,
    ) -> list[dict]:

        session = SessionLocal()

        try:

            records = (
                session.query(
                    WorkflowJournalRecord
                )
                .all()
            )

            result = []

            for record in records:

                result.append(
                    {
                        "journal_id":
                            record.journal_id,

                        "workflow_id":
                            record.workflow_id,

                        "workflow_name":
                            record.workflow_name,

                        "created_by":
                            record.created_by,

                        "status":
                            record.status,

                        "saved_at":
                            record.saved_at.isoformat(),

                        "executed_at":
                            (
                                record.executed_at
                                .isoformat()
                                if record.executed_at
                                else None
                            ),

                        "object_count":
                            record.object_count,

                        "step_count":
                            record.step_count,

                        "snapshot":
                            json.loads(
                                record.snapshot_json
                            ),
                    }
                )

            return result

        finally:
            session.close()

    def update_status(
        self,
        workflow_id: str,
        status: str,
        executed_at: datetime | None = None,
    ) -> bool:

        session = SessionLocal()

        try:

            record = (
                session.query(
                    WorkflowJournalRecord
                )
                .filter_by(
                    workflow_id=workflow_id
                )
                .first()
            )

            if not record:
                return False

            record.status = status
            record.executed_at = executed_at

            session.commit()

            return True

        finally:
            session.close()

    def delete_entry(
        self,
        journal_id: str,
    ) -> bool:

        session = SessionLocal()

        try:

            record = session.get(
                WorkflowJournalRecord,
                journal_id,
            )

            if not record:
                return False

            session.delete(record)

            session.commit()

            return True

        finally:
            session.close()