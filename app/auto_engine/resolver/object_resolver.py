from app.adapters.ldap_container import (
    ldap,
)

from app.search_tools.workflow_search_user import (
    workflow_search_user,
)

from app.search_tools.workflow_search_computer import (
    workflow_search_computer,
)
from app.search_tools.workflow_search_group import (
    workflow_search_group,
)

from app.search_tools.workflow_search_ou import (
    workflow_search_ou,
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
    Resolve exactly one COMPUTER business object
    for Workflow Engine.

    Resolution identity:
    - computer_name

    Fail-closed:
    - Missing identity: STOP
    - Search failure: STOP
    - 0 results: STOP
    - More than 1 result: STOP
    """

    computer_name = (
        source_data.get(
            "computer_name"
        )
    )

    if not computer_name:

        raise ValueError(
            "Missing computer_name"
        )

    result = workflow_search_computer(
        connection=
            ldap.connection,

        computer_name=
            computer_name,
    )

    # ==============================================
    # SEARCH FAILURE
    # ==============================================

    if not result["success"]:

        raise ValueError(
            "Workflow computer lookup failed: "
            f"{result.get('message', 'Unknown LDAP error')}"
        )

    count = (
        result["count"]
    )

    identity_field = (
        result.get(
            "identity_field"
        )
    )

    identity_value = (
        result.get(
            "identity_value"
        )
    )

    # ==============================================
    # NO MATCH
    # ==============================================

    if count == 0:

        raise ValueError(
            "Workflow computer resolution stopped: "
            f"no computer found for "
            f"{identity_field}={identity_value}"
        )

    # ==============================================
    # AMBIGUOUS MATCH
    # ==============================================

    if count > 1:

        raise ValueError(
            "Workflow computer resolution stopped: "
            f"{count} computers found for "
            f"{identity_field}={identity_value}. "
            "Expected exactly one computer."
        )

    # Đến đây count chắc chắn bằng 1.
    computer = (
        result["results"][0]
    )

    computer_name_value = (
        computer.get(
            "computer_name"
        )
    )

    distinguished_name = (
        computer.get(
            "distinguished_name"
        )
    )

    if not computer_name_value:

        raise ValueError(
            "Resolved computer missing "
            "computer_name"
        )

    if not distinguished_name:

        raise ValueError(
            "Resolved computer missing "
            "distinguished_name"
        )

    return {
        "object_type":
            "COMPUTER",

        "computer_name":
            computer_name_value,

        "sam_account_name":
            computer.get(
                "sam_account_name"
            ),

        "dns_host_name":
            computer.get(
                "dns_host_name"
            ),

        "description":
            computer.get(
                "description"
            ),

        "operating_system":
            computer.get(
                "operating_system"
            ),

        "dn":
            distinguished_name,
    }

def resolve_group(
    source_data: dict,
) -> dict:
    """
    Resolve exactly one GROUP business object
    for Workflow Engine.

    Resolution priority:
    1. group_name
    2. email

    Fail-closed:
    - 0 results: STOP
    - More than 1 result: STOP
    - Search failure: STOP
    """

    group_name = (
        source_data.get(
            "group_name"
        )
        or
        source_data.get(
            "groupName"
        )
    )

    email = (
        source_data.get(
            "email"
        )
        or
        source_data.get(
            "mail"
        )
    )

    if not group_name and not email:

        raise ValueError(
            "Missing group_name or email"
        )

    result = workflow_search_group(
        connection=ldap.connection,
        group_name=group_name,
        email=email,
    )

    # ==============================================
    # SEARCH FAILURE
    # ==============================================

    if not result["success"]:

        raise ValueError(
            "Workflow group lookup failed: "
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
    # NO MATCH
    # ==============================================

    if count == 0:

        raise ValueError(
            "Workflow group resolution stopped: "
            f"no group found for "
            f"{identity_field}={identity_value}"
        )

    # ==============================================
    # AMBIGUOUS MATCH
    # ==============================================

    if count > 1:

        raise ValueError(
            "Workflow group resolution stopped: "
            f"{count} groups found for "
            f"{identity_field}={identity_value}. "
            "Expected exactly one group."
        )

    # Đến đây count chắc chắn bằng 1.
    group = result["results"][0]

    return {
        "object_type":
            "GROUP",

        "display_name":
            group.get(
                "display_name"
            ),

        "group_name":
            (
                group.get(
                    "group_name"
                )
                or
                group.get(
                    "name"
                )
            ),

        "sam_account_name":
            group.get(
                "sam_account_name"
            ),

        "email":
            (
                group.get(
                    "mail"
                )
                or
                group.get(
                    "email"
                )
            ),

        "dn":
            (
                group.get(
                    "distinguished_name"
                )
                or
                group.get(
                    "dn"
                )
            ),
    }

def resolve_ou(
    source_data: dict,
) -> dict:
    """
    Resolve exactly one OU business object
    for Workflow Engine.

    Admin may provide a friendly OU name,
    for example:
        "Hội sở"

    The resolver returns the canonical
    distinguished name required by runtime.

    Fail-closed:
    - 0 results: STOP
    - More than 1 result: STOP
    - Search failure: STOP
    """

    ou_name = (
        source_data.get(
            "ou_name"
        )
        or
        source_data.get(
            "ouName"
        )
        or
        source_data.get(
            "target_ou"
        )
        or
        source_data.get(
            "targetOu"
        )
    )

    if not ou_name:

        raise ValueError(
            "Missing ou_name or target_ou"
        )

    result = workflow_search_ou(
        connection=ldap.connection,
        ou_name=ou_name,
    )

    # ==============================================
    # SEARCH FAILURE
    # ==============================================

    if not result["success"]:

        raise ValueError(
            "Workflow OU lookup failed: "
            f"{result.get('message', 'Unknown LDAP error')}"
        )

    count = result["count"]

    identity_field = result.get(
        "identity_field",
        "ou_name"
    )

    identity_value = result.get(
        "identity_value",
        ou_name
    )

    # ==============================================
    # NO MATCH
    # ==============================================

    if count == 0:

        raise ValueError(
            "Workflow OU resolution stopped: "
            f"no OU found for "
            f"{identity_field}={identity_value}"
        )

    # ==============================================
    # AMBIGUOUS MATCH
    # ==============================================

    if count > 1:

        matched_ous = [
            item.get(
                "distinguished_name"
            )
            for item in result["results"]
        ]

        raise ValueError(
            "Workflow OU resolution stopped: "
            f"{count} OUs found for "
            f"{identity_field}={identity_value}. "
            "Expected exactly one OU. "
            f"Matches: {matched_ous}"
        )

    # Đến đây count chắc chắn bằng 1.
    ou = result["results"][0]

    return {
        "object_type":
            "OU",

        "ou_name":
            ou["ou"],

        "dn":
            ou[
                "distinguished_name"
            ],
    }


OBJECT_RESOLVERS = {
    "resolve_user":
        resolve_user,

    "resolve_computer":
        resolve_computer,

    "resolve_group":
        resolve_group,

    "resolve_ou":
        resolve_ou,
}