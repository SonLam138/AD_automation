from .ad_service import (
    authenticate_and_get_profile
)

from app.config import (
    LOGIN_GROUP_LANDING_MAP
)


def resolve_landing_page(
    user_groups: list[str]
):

    for group, landing_page in LOGIN_GROUP_LANDING_MAP.items():

        if group in user_groups:
            return landing_page

    return None


def authenticate_user(
    username,
    password
):

    print("=" * 80)
    print("LOGIN USER =", username)
    print("=" * 80)

    user = authenticate_and_get_profile(
        username,
        password
    )

    print("LDAP RESULT =", user)

    if not user:
        return None

    user_groups = user.get(
        "groups",
        []
    )

    print("GROUPS =", user_groups)

    landing_page = resolve_landing_page(
        user_groups
    )

    if not landing_page:

        print(
            "LOGIN DENIED - no login group matched"
        )

        return None

    user["landing_page"] = landing_page

    print(
        "AUTH SUCCESS - landing_page =",
        landing_page
    )

    return user