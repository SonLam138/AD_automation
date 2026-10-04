from typing import Optional

from ldap3.utils.dn import escape_rdn, parse_dn
from ldap3.utils.conv import escape_filter_chars

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


def integration_resolve_ou(
    connection,
    target_ou: Optional[str] = None,
    target_ou_parent: Optional[str] = None,
) -> dict:
    normalized_ou = (
        target_ou.strip()
        if target_ou and target_ou.strip()
        else None
    )
    normalized_parent = (
        target_ou_parent.strip()
        if target_ou_parent and target_ou_parent.strip()
        else None
    )

    if not normalized_ou:
        return {
            "success": False,
            "identity_field": None,
            "identity_value": None,
            "count": 0,
            "results": [],
            "message": "Missing target_ou",
        }

    is_dn = normalized_ou.lower().startswith(
        ("ou=", "cn=", "dc=")
    )
    identity_field = (
        "distinguishedName"
        if is_dn
        else "ou"
    )
    safe_value = escape_filter_chars(normalized_ou)
    search_success = connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=(
            "(&(objectClass=organizationalUnit)"
            f"({identity_field}={safe_value}))"
        ),
        attributes=[
            "ou",
            "distinguishedName",
        ],
        size_limit=100,
    )

    if not search_success:
        return {
            "success": False,
            "identity_field": identity_field,
            "identity_value": normalized_ou,
            "count": 0,
            "results": [],
            "message": str(connection.result),
        }

    results = []
    escaped_parent = (
        escape_rdn(normalized_parent).casefold()
        if normalized_parent
        else None
    )

    for entry in connection.entries:
        distinguished_name = _get_attr_value(
            entry,
            "distinguishedName",
        )

        if normalized_parent:
            direct_parent = _direct_parent_ou(
                distinguished_name,
                "OU",
            )
            if (
                direct_parent is None
                or direct_parent.casefold() != escaped_parent
            ):
                continue

        results.append(
            {
                "object_type": "OU",
                "ou": _get_attr_value(entry, "ou"),
                "distinguished_name": distinguished_name,
            }
        )

    return {
        "success": True,
        "identity_field": identity_field,
        "identity_value": normalized_ou,
        "parent_ou": normalized_parent,
        "count": len(results),
        "results": results,
    }
