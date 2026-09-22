# app/auto_engine/sqlite/create_db.py

from app.auto_engine.sqlite.base import Base
from app.auto_engine.sqlite.db import engine

# quan trọng
from app.auto_engine.sqlite.execution_plan_record import (
    ExecutionPlanRecord,
)
from app.auto_engine.sqlite.workflow_journal_record import (
    WorkflowJournalRecord,
)
from app.auto_engine.sqlite.mail_request_audit_record import (
    MailRequestAuditRecord,
)

from app.auto_engine.sqlite.access_snapshot import AccessSnapshot

def create_database():

    Base.metadata.create_all(engine)

    print(
        "ExecutionPlan SQLite database created successfully."
    )


if __name__ == "__main__":
    create_database()