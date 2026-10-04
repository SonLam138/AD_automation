from typing import Optional

from ldap3.utils.conv import escape_filter_chars
from ldap3.utils.dn import escape_rdn, parse_dn

from app.config import LDAP_BASE_DN


def _get_attr_value(entry, attr_name: str) -> str:
    attribute = getattr(entry, attr_name, None)
    value = getattr(attribute, "value", None)
    return "" if value is None else str(value)


def _direct_parent_ou(
    distinguished_name: str,
    object_attribute: str,
) -> Optional[str]:
    try:
        rdns = parse_dn(distinguished_name)
    except (TypeError, ValueError):
        return None

    if (
        len(rdns) < 2
        or rdns[0][0].lower() != object_attribute.lower()
        or rdns[1][0].lower() != "ou"
    ):
        return None

    return rdns[1][1]


def _search_group(
    connection,
    identity_field: str,
    identity_value: str,
    size_limit: int = 2,
) -> dict:
    safe_value = escape_filter_chars(identity_value)
    identity_filter = f"({identity_field}={safe_value})"

    search_success = connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=(
            "(&(objectClass=group)"
            f"{identity_filter})"
        ),
        attributes=[
            "cn",
            "name",
            "mail",
            "description",
            "distinguishedName",
        ],
        size_limit=size_limit,
    )

    if not search_success:
        return {
            "success": False,
            "identity_field": identity_field,
            "identity_value": identity_value,
            "count": 0,
            "results": [],
            "message": str(connection.result),
        }

    results = [
        {
            "object_type": "GROUP",
            "name": _get_attr_value(entry, "name"),
            "cn": _get_attr_value(entry, "cn"),
            "mail": _get_attr_value(entry, "mail"),
            "description": _get_attr_value(
                entry,
                "description",
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
        "identity_field": identity_field,
        "identity_value": identity_value,
        "count": len(results),
        "results": results,
    }


def integration_resolve_group(
    connection,
    target_group: Optional[str] = None,
    target_group_email: Optional[str] = None,
    target_group_ou: Optional[str] = None,
) -> dict:
    normalized_group = (
        target_group.strip()
        if target_group and target_group.strip()
        else None
    )
    normalized_email = (
        target_group_email.strip()
        if target_group_email and target_group_email.strip()
        else None
    )
    normalized_group_ou = (
        target_group_ou.strip()
        if target_group_ou and target_group_ou.strip()
        else None
    )

    if (
        normalized_group
        and "@" in normalized_group
        and not normalized_email
    ):
        normalized_email = normalized_group
        normalized_group = None

    if not normalized_group and not normalized_email:
        return {
            "success": False,
            "identity_field": None,
            "identity_value": None,
            "count": 0,
            "results": [],
            "message": "Missing target_group or target_group_email",
        }

    if normalized_email:
        email_result = _search_group(
            connection,
            "mail",
            normalized_email,
            size_limit=(
                100
                if normalized_group_ou
                else 2
            ),
        )

        if not email_result["success"]:
            return email_result

        if email_result["count"] > 0 or not normalized_group:
            result = email_result
        else:
            result = _search_group(
                connection,
                "name",
                normalized_group,
                size_limit=(
                    100
                    if normalized_group_ou
                    else 2
                ),
            )
    else:
        result = _search_group(
            connection,
            "name",
            normalized_group,
            size_limit=(
                100
                if normalized_group_ou
                else 2
            ),
        )

    if not normalized_group_ou or not result["success"]:
        return result

    expected_parent = escape_rdn(
        normalized_group_ou
    ).casefold()
    results = [
        group
        for group in result["results"]
        if (
            (
                parent_ou := _direct_parent_ou(
                    group["distinguished_name"],
                    "CN",
                )
            )
            is not None
            and parent_ou.casefold() == expected_parent
        )
    ]

    return {
        **result,
        "parent_ou": normalized_group_ou,
        "count": len(results),
        "results": results,
    }
