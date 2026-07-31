from app.adapters.ldap_adapter import LDAPAdapter

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


def test_disable_user():

    result = ldap.disable_user(
        "DuongNH"
    )

    print(result)


def test_update_user_displayname():

    result = ldap.update_user_displayname(
        "ad.auto4",
        "AD Automation_test(K.CNTT-HCM)"
    )

    print(result)


TEST_MAP = {

    "disable_user":
        test_disable_user,

    "update_user_displayname":
        test_update_user_displayname,
}


if __name__ == "__main__":

    TEST_MAP[
        "update_user_displayname"
    ]()