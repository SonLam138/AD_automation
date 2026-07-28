import json

from app.adapters.ldap_adapter import (
    LDAPAdapter
)

from app.search_tools.computer_search import (
    search_computer
)

from app.config import (
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)


ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)


print("=" * 60)
print("TEST SEARCH COMPUTER")
print("=" * 60)

keyword = input(
    "Computer keyword: "
).strip()

result = search_computer(
    connection=ldap.connection,
    keyword=keyword,
    limit=20
)

print(
    json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    )
)

print("=" * 60)
print("RESULT COUNT =", result["count"])
print("=" * 60)
