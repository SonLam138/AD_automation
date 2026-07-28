from ldap3.utils.conv import escape_filter_chars

from app.config import (
    LDAP_BASE_DN
)
def _get_attr_value(
    entry,
    attr_name,
    default=""
):
    """
    Safely get ldap3 entry attribute value.
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

    return str(value)


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

def search_computer(
    connection,
    keyword: str,
    limit: int = 10
):
    """
    Internal search tool for Agent.

    Purpose:
    - Resolve human input into AD computer candidate(s)
    - No API
    - No RBAC here
    - No LDAP modify
    - No action

    Search fields:
    - dNSHostName
    """

    if not keyword:
        return {
            "success": False,
            "keyword": keyword,
            "count": 0,
            "results": [],
            "message": "Keyword is empty"
        }

    safe_keyword = escape_filter_chars(
        keyword.strip()
    )

    search_filter = (
        "(&"
            "(objectCategory=computer)"
            "(objectClass=computer)"
            f"(dNSHostName=*{safe_keyword}*)"
        ")"
    )

    connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=search_filter,
        attributes=[
            "cn",
            "dNSHostName",
            "distinguishedName",
            "userAccountControl"
        ],
        size_limit=limit
    )

    results = []

    for entry in connection.entries:

        uac = _get_attr_value(
            entry,
            "userAccountControl",
            ""
        )

        item = {
            "object_type":
                "COMPUTER",

            "computer_name":
                _get_attr_value(
                    entry,
                    "cn"
                ),

            "dns_host_name":
                _get_attr_value(
                    entry,
                    "dNSHostName"
                ),

            "distinguished_name":
                _get_attr_value(
                    entry,
                    "distinguishedName"
                ),

            "user_account_control":
                uac,

            "is_disabled":
                _is_disabled(
                    uac
                )
        }

        results.append(
            item
        )

    return {
        "success": True,
        "keyword": keyword,
        "count": len(results),
        "results": results
    }