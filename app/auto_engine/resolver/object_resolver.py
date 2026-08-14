from app.adapters.ldap_container import (
    ldap,
)

from app.search_tools.user_search import (
    search_user,
)

from app.search_tools.computer_search import (
    search_computer,
)

def resolve_user(
    source_data: dict,
) -> dict:
    """
    Resolve business object USER
    cho Workflow Engine.

    Input:
        employee_id / email

    Output:
        target_object
    """

    keyword = (
        source_data.get("email")
        or source_data.get("employee_id")
    )

    if not keyword:
        raise ValueError(
            "Missing employee_id or email"
        )

    result = search_user(
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
            f"User not found: {keyword}"
        )

    user = result["results"][0]

    return {
        "object_type": "USER",

        "display_name":
            user["display_name"],

        "sam_account_name":
            user["sam_account_name"],

        "email":
            user["mail"],

        "dn":
            user["distinguished_name"],
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