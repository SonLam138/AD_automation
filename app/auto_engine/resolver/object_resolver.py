from app.adapters.ldap_container import (
    ldap,
)

from app.search_tools.workflow_search_user import (
    workflow_search_user,
)

from app.search_tools.computer_search import (
    search_computer,
)

def resolve_user(
    source_data: dict,
) -> dict:
    """
    Resolve exactly one USER business object
    for Workflow Engine.

    Resolution priority:
    1. employee_id
    2. email

    Fail-closed:
    - 0 results: STOP
    - More than 1 result: STOP
    - Search failure: STOP
    """

    employee_id = source_data.get(
        "employee_id"
    )

    email = source_data.get(
        "email"
    )

    if not employee_id and not email:
        raise ValueError(
            "Missing employee_id or email"
        )

    result = workflow_search_user(
        connection=ldap.connection,
        employee_id=employee_id,
        email=email,
    )

    # ==============================================
    # SEARCH FAILURE
    # ==============================================

    if not result["success"]:
        raise ValueError(
            "Workflow user lookup failed: "
            f"{result.get('message', 'Unknown LDAP error')}"
        )

    count = result["count"]

    identity_field = result.get(
        "identity_field"
    )

    identity_value = result.get(
        "identity_value"
    )

    # ==============================================
    # NO MATCH - STOP
    # ==============================================

    if count == 0:
        raise ValueError(
            "Workflow user resolution stopped: "
            f"no user found for "
            f"{identity_field}={identity_value}"
        )

    # ==============================================
    # AMBIGUOUS MATCH - STOP IMMEDIATELY
    # ==============================================

    if count > 1:
        raise ValueError(
            "Workflow user resolution stopped: "
            f"{count} users found for "
            f"{identity_field}={identity_value}. "
            "Expected exactly one user."
        )

    # Đến đây count chắc chắn bằng 1.
    user = result["results"][0]

    return {
        "object_type":
            "USER",

        "display_name":
            user["display_name"],

        "sam_account_name":
            user["sam_account_name"],

        "email":
            user["mail"],

        "dn":
            user["distinguished_name"],

        "member_of":
            user.get(
                "member_of",
                []
            ),
    }


def resolve_computer(
    source_data: dict,
) -> dict:
    """
    Resolve business object COMPUTER
    cho Workflow Engine.
    """

    keyword = (
        source_data.get(
            "computer_name"
        )
    )

    if not keyword:
        raise ValueError(
            "Missing computer_name"
        )

    result = search_computer(
        connection=ldap.connection,
        keyword=keyword,
        limit=1,
    )

    if not result["success"]:
        raise ValueError(
            f"Search failed: {keyword}"
        )

    if result["count"] == 0:
        raise ValueError(
            f"Computer not found: {keyword}"
        )

    computer = result["results"][0]

    return {
        "object_type": "COMPUTER",

        "computer_name":
            computer["computer_name"],

        "dns_host_name":
            computer["dns_host_name"],

        "distinguished_name":
            computer["distinguished_name"],
    }