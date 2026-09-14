# test_exchange.py

from app.adapters.get_mailbox import execute as get_mailbox
from app.adapters.disable_mailbox import execute as disable_mailbox

IDENTITY = "ad.auto2"


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


try:

    # STEP 1 - Validate mailbox
    print_section("STEP 1 - GET MAILBOX")

    mailbox = get_mailbox(IDENTITY)

    print(mailbox)

    # STEP 2 - Disable mailbox
    print_section("STEP 2 - DISABLE MAILBOX")

    result = disable_mailbox(IDENTITY)

    print(result)

    # STEP 3 - Verify again
    print_section("STEP 3 - GET MAILBOX AGAIN")

    mailbox_after = get_mailbox(IDENTITY)

    print(mailbox_after)

except Exception as ex:
    print_section("ERROR")
    print(str(ex))




