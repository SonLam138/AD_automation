from app.auto_engine.sqlite.db import SessionLocal
from app.auto_engine.sqlite.execution_plan_record import (
    ExecutionPlanRecord
)

session = SessionLocal()

record = (
    session.get(
        ExecutionPlanRecord,
        "REQ_01092026_492F"
    )
)

if record:

    print(
        record.execution_json
    )

session.close()