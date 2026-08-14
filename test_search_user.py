from app.auto_engine.actions.ad_actions import (
    DisableUserAction,
)

action = DisableUserAction()

result = action.execute(
    sam_account_name="ad.auto2"
)

print(result)