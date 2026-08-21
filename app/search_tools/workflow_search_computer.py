from typing import Optional

from ldap3.utils.conv import (
    escape_filter_chars
)

from app.config import (
    LDAP_BASE_DN
)


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
# WORKFLOW SEARCH COMPUTER
# ==================================================

def workflow_search_computer(
    connection,
    computer_name: Optional[str] = None,
) -> dict:
    """
    Resolve exactly one AD computer
    for Workflow Engine.

    Matching rules:
    - computer name exact match
    - sAMAccountName exact match
    - no wildcard
    - no fuzzy search
    - no ranking
    - no automatic selection
    """

    normalized_computer_name = (
        computer_name.strip()
        if computer_name
        else None
    )

    if not normalized_computer_name:

        return {
            "success": False,
            "identity_field":
                None,
            "identity_value":
                None,
            "count":
                0,
            "results":
                [],
            "message":
                "Missing computer_name"
        }

    safe_value = escape_filter_chars(
        normalized_computer_name
    )

    identity_field = (
        "computer_name"
    )

    identity_value = (
        normalized_computer_name
    )

    search_filter = (
        "(&"
            "(objectClass=computer)"
            "(|"
                f"(name={safe_value})"
                f"(sAMAccountName={safe_value})"
                f"(sAMAccountName={safe_value}$)"
            ")"
        ")"
    )

    search_success = connection.search(
        search_base=
            LDAP_BASE_DN,

        search_filter=
            search_filter,

        attributes=[
            "name",
            "sAMAccountName",
            "distinguishedName",
            "description",
            "operatingSystem",
            "dNSHostName",
        ],

        size_limit=
            2,
    )

    if not search_success:

        return {
            "success": False,

            "identity_field":
                identity_field,

            "identity_value":
                identity_value,

            "count":
                0,

            "results":
                [],

            "message":
                str(
                    connection.result
                ),
        }

    results = []

    for entry in connection.entries:

        results.append(
            {
                "object_type":
                    "COMPUTER",

                "computer_name":
                    _get_attr_value(
                        entry,
                        "name",
                    ),

                "sam_account_name":
                    _get_attr_value(
                        entry,
                        "sAMAccountName",
                    ),

                "dns_host_name":
                    _get_attr_value(
                        entry,
                        "dNSHostName",
                    ),

                "description":
                    _get_attr_value(
                        entry,
                        "description",
                    ),

                "operating_system":
                    _get_attr_value(
                        entry,
                        "operatingSystem",
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