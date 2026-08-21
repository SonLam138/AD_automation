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

    return str(value)


# ==================================================
# WORKFLOW SEARCH GROUP
# ==================================================

def workflow_search_group(
    connection,
    email: Optional[str] = None,
    group_name: Optional[str] = None,
) -> dict:
    """
    Resolve exactly one AD group for Workflow Engine.

    Matching priority:
    1. mail exact match
    2. name exact match

    Important:
    - No wildcard
    - No fuzzy search
    - No result ranking
    - No automatic selection
    - The caller must require exactly one result
    """

    normalized_email = (
        email.strip()
        if email
        else None
    )

    normalized_group_name = (
        group_name.strip()
        if group_name
        else None
    )

    # ==============================================
    # BUILD EXACT SEARCH FILTER
    # ==============================================

    if normalized_email:

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

    elif normalized_group_name:

        identity_field = (
            "name"
        )

        identity_value = (
            normalized_group_name
        )

        safe_value = escape_filter_chars(
            normalized_group_name
        )

        identity_filter = (
            f"(name={safe_value})"
        )

    else:

        return {
            "success": False,
            "identity_field": None,
            "identity_value": None,
            "count": 0,
            "results": [],
            "message": (
                "Missing email or group_name"
            )
        }

    search_filter = (
        "(&"
            "(objectClass=group)"
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
            "cn",
            "name",
            "mail",
            "description",
            "distinguishedName",
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

        results.append(
            {
                "object_type":
                    "GROUP",

                "name":
                    _get_attr_value(
                        entry,
                        "name",
                    ),

                "cn":
                    _get_attr_value(
                        entry,
                        "cn",
                    ),

                "mail":
                    _get_attr_value(
                        entry,
                        "mail",
                    ),

                "description":
                    _get_attr_value(
                        entry,
                        "description",
                    ),

                "distinguished_name":
                    _get_attr_value(
                        entry,
                        "distinguishedName",
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