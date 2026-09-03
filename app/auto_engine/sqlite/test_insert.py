from app.auto_engine.sqlite.db import SessionLocal
from app.auto_engine.sqlite.execution_plan_record import (
    ExecutionPlanRecord
)

session = SessionLocal()

records = (
    session.query(
        ExecutionPlanRecord
    )
    .filter_by(
        target_account="ad.auto3"
    )
    .all()
)

for record in records:

    print(
        record.workflow_id,
        record.target_object_type,
        record.target_account,
    )

session.close()