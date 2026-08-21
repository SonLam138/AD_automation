from ldap3.utils.conv import (
    escape_filter_chars
)

from app.config import (
    LDAP_BASE_DN
)


def workflow_search_ou(
    connection,
    ou_name: str
):
    """
    Workflow OU resolver search.

    Resolution target:
    - Exact OU business object

    Fail closed:
    - return count
    - caller decides stop/pass
    """

    if not ou_name:
        return {
            "success": False,
            "message": "Missing ou_name"
        }

    safe_keyword = (
        escape_filter_chars(
            ou_name.strip()
        )
    )

    search_filter = (
        "(|"
        f"(ou={safe_keyword})"
        f"(ou=*{safe_keyword}*)"
        ")"
    )

    connection.search(
        search_base=LDAP_BASE_DN,
        search_filter=search_filter,
        attributes=[
            "ou",
            "distinguishedName"
        ],
        size_limit=20
    )

    results = []

    for entry in connection.entries:

        results.append(
            {
                "object_type": "OU",

                "ou":
                    str(
                        entry.ou.value
                    ),

                "distinguished_name":
                    str(
                        entry
                        .distinguishedName
                        .value
                    )
            }
        )

    return {
        "success": True,

        "identity_field":
            "ou_name",

        "identity_value":
            ou_name,

        "count":
            len(results),

        "results":
            results
    }