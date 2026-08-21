from typing import Optional

from ldap3.utils.conv import (
    escape_filter_chars
)

from app.config import (
    LDAP_BASE_DN
)

# ==================================================
# LDAP ATTRIBUTE HELPERS
# ==================================================

def _get_attr_value(
    entry,
    attr_name: str,
    default=""
):
    """
    Safely get a single ldap3 entry attribute value.
    """

    if not hasattr(
        entry,
        attr_name
    ):
        return default

    attr = getattr(
        entry,
        attr_name
    )

    value = attr.value

    if value is None:
        return default

    return str(
        value
    )


def _get_attr_values(
    entry,
    attr_name: str
) -> list:
    """
    Safely get a multi-value ldap3 entry attribute.
    """

    if not hasattr(
        entry,
        attr_name
    ):
        return []

    attr = getattr(
        entry,
        attr_name
    )

    values = attr.values

    if not values:
        return []

    return [
        str(value)
        for value in values
    ]


def _is_disabled(
    user_account_control
):
    """
    Check AD ACCOUNTDISABLE bit.

    ACCOUNTDISABLE = 2
    """

    try:
        uac = int(
            user_account_control
        )

        return bool(
            uac & 2
        )

    except Exception:
        return None


# ==================================================
# WORKFLOW SEARCH USER
# ==================================================

def workflow_search_user(
    connection,
    employee_id: Optional[str] = None,
    email: Optional[str] = None,
) -> dict:
    """
    Resolve exactly one AD user for Workflow Engine.

    Matching priority:
    1. employeeID exact match
    2. mail exact match

    Important:
    - No wildcard
    - No fuzzy search
    - No result ranking
    - No automatic selection
    - The caller must require exactly one result
    """

    normalized_employee_id = (
        employee_id.strip()
        if employee_id
        else None
    )

    normalized_email = (
        email.strip()
        if email
        else None
    )

    # ==============================================
    # BUILD EXACT SEARCH FILTER
    # ==============================================

    if normalized_employee_id:

        identity_field = (
            "employeeID"
        )

        identity_value = (
            normalized_employee_id
        )

        safe_value = escape_filter_chars(
            normalized_employee_id
        )

        identity_filter = (
            f"(employeeID={safe_value})"
        )

    elif normalized_email:

        identity_field = (
            "mail"
        )

        identity_value = (
            normalized_email
        )

        safe_value = escape_filter_chars(
            normalized_email
        )

        identity_filter = (
            f"(mail={safe_value})"
        )

    else:

        return {
            "success": False,
            "identity_field": None,
            "identity_value": None,
            "count": 0,
            "results": [],
            "message": (
                "Missing employee_id or email"
            )
        }

    search_filter = (
        "(&"
            "(objectCategory=person)"
            "(objectClass=user)"
            f"{identity_filter}"
        ")"
    )

    # ==============================================
    # LDAP SEARCH
    # ==============================================

    search_success = connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=search_filter,
        attributes=[
            "displayName",
            "sAMAccountName",
            "employeeID",
            "mail",
            "distinguishedName",
            "userAccountControl",
            "department",
            "title",
            "memberOf",
        ],
        size_limit=2,
    )

    if not search_success:

        return {
            "success": False,
            "identity_field":
                identity_field,
            "identity_value":
                identity_value,
            "count": 0,
            "results": [],
            "message":
                str(connection.result),
        }

    # ==============================================
    # BUILD RESULT
    # ==============================================

    results = []

    for entry in connection.entries:

        user_account_control = (
            _get_attr_value(
                entry,
                "userAccountControl",
                "",
            )
        )

        results.append(
            {
                "object_type":
                    "USER",

                "display_name":
                    _get_attr_value(
                        entry,
                        "displayName",
                    ),

                "sam_account_name":
                    _get_attr_value(
                        entry,
                        "sAMAccountName",
                    ),

                "employee_id":
                    _get_attr_value(
                        entry,
                        "employeeID",
                    ),

                "mail":
                    _get_attr_value(
                        entry,
                        "mail",
                    ),

                "department":
                    _get_attr_value(
                        entry,
                        "department",
                    ),

                "title":
                    _get_attr_value(
                        entry,
                        "title",
                    ),

                "distinguished_name":
                    _get_attr_value(
                        entry,
                        "distinguishedName",
                    ),

                "user_account_control":
                    user_account_control,

                "is_disabled":
                    _is_disabled(
                        user_account_control
                    ),

                "member_of":
                    _get_attr_values(
                        entry,
                        "memberOf",
                    ),
            }
        )

    return {
        "success": True,
        "identity_field":
            identity_field,
        "identity_value":
            identity_value,
        "count":
            len(results),
        "results":
            results,
    }