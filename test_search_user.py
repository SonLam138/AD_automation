from app.adapters.ldap_adapter import (
    LDAPAdapter
)

from app.search_tools import (
    search_group
)
from app.search_tools import search_ou
from app.config import (
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)

from app.search_tools import (
    search_user
)


ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)

# result = search_user(
#     ldap.connection,
#     "ad.auto",
#     limit=20
# )

# print(result)


# result = search_group(
#     ldap.connection,
#     "test"
# )

# print(result)

result = search_ou(
    ldap.connection,
    "HO"
)

print(result)