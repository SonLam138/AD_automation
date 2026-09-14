from app.adapters.ldap_container import ldap

from app.search_tools.workflow_search_user import (
    workflow_search_user
)

print(type(ldap))
print(vars(ldap))
def print_user(result):

    if not result["success"]:
        print(result)
        return

    if result["count"] != 1:
        print(result)
        return

    user = result["results"][0]

    print("========================================")
    print("USER")
    print("========================================")

    print(
        "DISPLAY NAME:",
        user["display_name"]
    )

    print(
        "SAM ACCOUNT:",
        user["sam_account_name"]
    )

    print(
        "MAIL:",
        user["mail"]
    )

    print(
        "IS DISABLED:",
        user["is_disabled"]
    )

    print(
        "REMOTE RECIPIENT TYPE:",
        user.get(
            "ms_exch_remote_recipient_type"
        )
    )

    print(
        "TARGET ADDRESS:",
        user.get(
            "target_address"
        )
    )

    print(
        "IS REMOTE MAILBOX:",
        user.get(
            "is_remote_mailbox"
        )
    )

    print()


def main():

    #connection = get_connection()

    # ==========================================
    # USER THƯỜNG
    # ==========================================

    print()
    print("========================================")
    print("NORMAL USER")
    print("========================================")

    result = workflow_search_user(
        ldap.connection,
        email="ad.auto1@automate.com.vn"
    )

    print_user(result)

    # ==========================================
    # REMOTE MAILBOX
    # ==========================================

    print()
    print("========================================")
    print("REMOTE MAILBOX USER")
    print("========================================")

    result = workflow_search_user(
        ldap.connection,
        email="ad.auto2@automate.com.vn"
    )

    print_user(result)


if __name__ == "__main__":
    main()