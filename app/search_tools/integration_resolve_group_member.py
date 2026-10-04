from typing import Optional

from ldap3.utils.conv import escape_filter_chars

from app.config import LDAP_BASE_DN
from app.search_tools.integration_resolve_group import (
    integration_resolve_group,
)


def _get_attr_value(entry, attr_name: str) -> str:
    attribute = getattr(entry, attr_name, None)
    value = getattr(attribute, "value", None)
    return "" if value is None else str(value)


def _resolve_user(
    connection,
    sam_account_name: str,
) -> dict:
    normalized_name = sam_account_name.strip()
    if not normalized_name:
        return {
            "success": False,
            "identity_field": "sAMAccountName",
            "identity_value": normalized_name,
            "count": 0,
            "results": [],
            "message": "Missing sam_account_name",
        }

    safe_name = escape_filter_chars(normalized_name)
    search_success = connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=(
            "(&(objectCategory=person)"
            "(objectClass=user)"
            f"(sAMAccountName={safe_name}))"
        ),
        attributes=[
            "sAMAccountName",
            "distinguishedName",
        ],
        size_limit=2,
    )

    if not search_success:
        return {
            "success": False,
            "identity_field": "sAMAccountName",
            "identity_value": normalized_name,
            "count": 0,
            "results": [],
            "message": str(connection.result),
        }

    results = [
        {
            "object_type": "USER",
            "sam_account_name": _get_attr_value(
                entry,
                "sAMAccountName",
            ),
            "distinguished_name": _get_attr_value(
                entry,
                "distinguishedName",
            ),
        }
        for entry in connection.entries
    ]

    return {
        "success": True,
        "identity_field": "sAMAccountName",
        "identity_value": normalized_name,
        "count": len(results),
        "results": results,
    }


def integration_resolve_computer(
    connection,
    computer_name: str,
) -> dict:
    normalized_name = computer_name.strip()
    if normalized_name.endswith("$"):
        normalized_name = normalized_name[:-1]

    safe_name = escape_filter_chars(normalized_name)
    search_success = connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=(
            "(&(objectClass=computer)"
            "(|"
            f"(name={safe_name})"
            f"(sAMAccountName={safe_name}$)"
            ")"
            ")"
        ),
        attributes=[
            "name",
            "sAMAccountName",
            "distinguishedName",
        ],
        size_limit=2,
    )

    if not search_success:
        return {
            "success": False,
            "identity_field": "computer_name",
            "identity_value": normalized_name,
            "count": 0,
            "results": [],
            "message": str(connection.result),
        }

    results = [
        {
            "object_type": "COMPUTER",
            "computer_name": _get_attr_value(
                entry,
                "name",
            ),
            "sam_account_name": _get_attr_value(
                entry,
                "sAMAccountName",
            ),
            "distinguished_name": _get_attr_value(
                entry,
                "distinguishedName",
            ),
        }
        for entry in connection.entries
    ]

    return {
        "success": True,
        "identity_field": "computer_name",
        "identity_value": normalized_name,
        "count": len(results),
        "results": results,
    }


def integration_resolve_group_member(
    connection,
    object_type: str,
    sam_account_name: Optional[str] = None,
    computer_name: Optional[str] = None,
    group_name: Optional[str] = None,
    group_email: Optional[str] = None,
    group_ou: Optional[str] = None,
) -> dict:
    if object_type == "user":
        if not sam_account_name:
            return {
                "success": False,
                "identity_field": "sAMAccountName",
                "identity_value": None,
                "count": 0,
                "results": [],
                "message": "Missing sam_account_name",
            }

        return _resolve_user(
            connection,
            sam_account_name,
        )

    if object_type == "computer":
        if not computer_name:
            return {
                "success": False,
                "identity_field": "computer_name",
                "identity_value": None,
                "count": 0,
                "results": [],
                "message": "Missing computer_name",
            }

        return integration_resolve_computer(
            connection,
            computer_name,
        )

    if object_type == "group":
        return integration_resolve_group(
            connection,
            target_group=group_name,
            target_group_email=group_email,
            target_group_ou=group_ou,
        )

    return {
        "success": False,
        "identity_field": None,
        "identity_value": object_type,
        "count": 0,
        "results": [],
        "message": f"Unsupported member object_type: {object_type}",
    }
