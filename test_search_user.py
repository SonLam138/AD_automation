from app.auto_engine.actions.ad_actions import (
    DisableUserAction,
)
from app.adapters.ldap_container import ldap
from app.search_tools.workflow_search_user import workflow_search_user


user = workflow_search_user(
    ldap.connection,
    employee_id="",
    email="sonnm@automate.com.vn"
    )


print(user)



# action = DisableUserAction()

# result = action.execute(
#     sam_account_name="ad.auto2"
# )

# print(result)