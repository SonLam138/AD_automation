from ldap3.utils.conv import (
    escape_filter_chars
)

from app.config import (
    LDAP_BASE_DN
)


def _get_attr_value(
    entry,
    attr_name,
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


def search_group(
    connection,
    keyword: str,
    limit: int = 100
):

    if not keyword:

        return {
            "success": False,
            "keyword": keyword,
            "count": 0,
            "results": []
        }

    safe_keyword = escape_filter_chars(
        keyword.strip()
    )

    search_filter = (
        "(&"
            "(objectClass=group)"
            "(|"
                f"(cn=*{safe_keyword}*)"
                f"(name=*{safe_keyword}*)"
                f"(description=*{safe_keyword}*)"
                f"(mail=*{safe_keyword}*)"
            ")"
        ")"
    )

    connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=search_filter,
        attributes=[
            "cn",
            "name",
            "description",
            "mail",
            "distinguishedName"
        ],
        size_limit=limit
    )

    results = []

    for entry in connection.entries:

        results.append(
            {
                "object_type": "GROUP",

                "name": _get_attr_value(
                    entry,
                    "name"
                ),

                "cn": _get_attr_value(
                    entry,
                    "cn"
                ),

                "description":
                    _get_attr_value(
                        entry,
                        "description"
                    ),

                "mail":
                    _get_attr_value(
                        entry,
                        "mail"
                    ),

                "distinguished_name":
                    _get_attr_value(
                        entry,
                        "distinguishedName"
                    )
            }
        )

    return {
        "success": True,
        "keyword": keyword,
        "count": len(results),
        "results": results
    }