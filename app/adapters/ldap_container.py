from app.adapters.ldap_adapter import (
    LDAPAdapter,
)

from app.config import (
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD,
)


ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD,
)