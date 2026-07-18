from ldap3.utils.conv import (
    escape_filter_chars
)

from app.config import (
    LDAP_BASE_DN
)

def search_ou(
    connection,
    keyword: str,
    limit: int = 100
):

    safe_keyword = (
        escape_filter_chars(
            keyword.strip()
        )
    )

    search_filter = (
        "(|"
            f"(ou=*{safe_keyword}*)"
            f"(distinguishedName=*{safe_keyword}*)"
        ")"
    )

    connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=search_filter,
        attributes=[
            "ou",
            "distinguishedName"
        ],
        size_limit=limit
    )

    results = []

    for entry in connection.entries:

        results.append(
            {
                "object_type":
                    "OU",

                "ou":
                    str(entry.ou.value),

                "distinguished_name":
                    str(
                        entry.distinguishedName.value
                    )
            }
        )

    return {
        "success": True,
        "keyword": keyword,
        "count": len(results),
        "results": results
    }