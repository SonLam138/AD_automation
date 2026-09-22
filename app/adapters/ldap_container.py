from app.adapters.ldap_adapter import (
    LDAPAdapter,
)

from app.config import (
    LDAP_HOST,
    LDAP_USER,
)

from app.security.ldap_credential_provider import (
    LdapCredentialProvider
)






ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,

    LDAP_USER,

    LdapCredentialProvider.get_password(),
)