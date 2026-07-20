import json

from app.agent.run_agent import (
    resolve_action,
    handle_user_input
)

from app.agent.action_handle import (
    execute_action
)

from app.adapters.ldap_adapter import (
    LDAPAdapter
)

from app.config import *


def print_step(
    title: str,
    data: dict
):
    print("\n")
    print("=" * 80)
    print(title)
    print("=" * 80)

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )
    )


def test_sensitive_flow():

    ldap = LDAPAdapter()

    ldap.connect(
        LDAP_HOST,
        LDAP_USER,
        LDAP_PASSWORD
    )

    #
    # TURN 1
    #
    result = resolve_action(
        user_text="disable sonnm",
        ldap_connection=ldap.connection
    )

    print_step(
        "TURN 1 - RESOLVE",
        result
    )

    action_id = result["action_id"]

    #
    # TURN 2
    # User: đồng ý
    #
    result = handle_user_input(
        action_id,
        "đồng ý"
    )

    print_step(
        "TURN 2 - CONFIRM",
        result
    )

    #
    # TURN 3
    # User: nhập secret
    #
    result = handle_user_input(
        action_id,
        ADMIN_APPROVAL_SECRET
    )

    print_step(
        "TURN 3 - SECRET",
        result
    )

    #
    # TURN 4
    # Execute
    #
    result = execute_action(
        action_id
    )

    print_step(
        "TURN 4 - EXECUTE",
        result
    )


if __name__ == "__main__":
    test_sensitive_flow()