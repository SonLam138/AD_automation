from app.agent.execution_response import (
    generate_execution_response
)

test_cases = [

    {
        "state": "ACTION_SUCCESS",
        "action": "disable_user",
        "execution_result": {
            "success": True,
            "action": "disable_user",
            "sam_account_name": "Onboard.approve",
            "user_dn": (
                "CN=Onboard Approver,"
                "OU=HO,"
                "DC=automate,"
                "DC=com,"
                "DC=vn"
            )
        }
    },

    {
        "state": "ACTION_SUCCESS",
        "action": "add_group",
        "execution_result": {
            "success": True,
            "action": "add_group",
            "sam_account_name": "sonnm",
            "group_name": "VPN Users"
        }
    },

    {
        "state": "ACTION_FAILED",
        "action": "disable_user",
        "execution_result": {
            "success": False,
            "error": (
                "User not found"
            )
        }
    }
]

for case in test_cases:

    print("=" * 80)

    print("EXECUTION CONTRACT")

    print(case)

    print()

    print("COPILOT RESPONSE")

    response = generate_execution_response(
        case
    )

    print(response)

    print()