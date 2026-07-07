from ldap3 import Server
from ldap3 import Connection
from ldap3 import ALL

from app.LDAPConfig.ad_config import (
    LDAP_SERVER,
    BASE_DN,
    SERVICE_ACCOUNT,
    SERVICE_PASSWORD
)


from ldap3 import Server
from ldap3 import Connection
from ldap3 import ALL

from app.LDAPConfig.ad_config import (
    LDAP_SERVER,
    BASE_DN,
    SERVICE_ACCOUNT,
    SERVICE_PASSWORD
)


def authenticate_and_get_profile(
    username: str,
    password: str
):

    try:

        server = Server(
            LDAP_SERVER,
            get_info=ALL
        )

        print("STEP 1 - Service Bind")

        svc_conn = Connection(
            server,
            user=SERVICE_ACCOUNT,
            password=SERVICE_PASSWORD,
            auto_bind=True
        )

        print("Service Bind OK")

        print(f"SEARCH USER = {username}")

        svc_conn.search(
            search_base=BASE_DN,
            search_filter=f"(sAMAccountName={username})",
            attributes=[
                "displayName",
                "mail",
                "memberOf",
                "distinguishedName"
            ]
        )

        print(
            f"SEARCH RESULT COUNT = {len(svc_conn.entries)}"
        )

        if not svc_conn.entries:
            print("USER NOT FOUND")
            return None

        entry = svc_conn.entries[0]

        user_dn = str(
            entry.distinguishedName
        )

        print(f"USER DN = {user_dn}")

        print("STEP 2 - User Bind")

        try:

            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )

            print("User Bind OK")

        except Exception as ex:

            print("User Bind FAIL")
            print(repr(ex))

            return None

        groups = []

        if hasattr(entry, "memberOf"):

            for group_dn in entry.memberOf:

                group_name = (
                    str(group_dn)
                    .split(",")[0]
                    .replace("CN=", "")
                )

                groups.append(
                    group_name
                )

        print("USER GROUPS =", groups)

        return {

            "username": username,

            "display_name": (
                str(entry.displayName)
                if hasattr(entry, "displayName")
                else username
            ),

            "email": (
                str(entry.mail)
                if hasattr(entry, "mail")
                else ""
            ),

            "groups": groups

        }

    except Exception as ex:

        print("LDAP ERROR")
        print(repr(ex))

        return None
