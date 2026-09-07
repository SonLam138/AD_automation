from app.adapters.ldap_container import ldap
from app.auto_engine.models.employee_offboarding import EmployeeOffboardingApiRequest
from app.search_tools.user_search import search_user

from app.ra_soat.off_ra_soat_model import (
    RelatedAccountSearchResult,
    RaSoatOffboardingSourceUser
)
from datetime import (
    datetime,
    timedelta,
)

ACCOUNT_PREFIXES = [
    "ad.",
    "pad.",
]

def generate_effective_time() -> str:
    return (
        datetime.now()
        + timedelta(minutes=30)
    ).isoformat(
        timespec="seconds"
    )


def generate_search_keys(
    username: str,
) -> list:
    return [
        f"{prefix}{username}"
        for prefix in ACCOUNT_PREFIXES
    ]


def search_related_account(
    search_key: str,
) -> RelatedAccountSearchResult:

    normalized_search_key = (
        search_key.strip().lower()
    )

    search_result = search_user(
        connection=ldap.connection,
        keyword=normalized_search_key,
        limit=10,
        include_excluded_ou=True,
    )

    if not search_result.get(
        "success"
    ):
        return RelatedAccountSearchResult(
            search_key=normalized_search_key,
            found=False,
            sam_account_name=None,
            email=None,
            is_disabled=None,
        )

    for item in search_result.get(
        "results",
        [],
    ):
        sam_account_name = (
            item.get(
                "sam_account_name",
                "",
            )
            .strip()
            .lower()
        )

        if (
            sam_account_name
            != normalized_search_key
        ):
            continue

        email = (
            item.get(
                "mail",
                "",
            )
            .strip()
            .lower()
        )

        return RelatedAccountSearchResult(
            search_key=normalized_search_key,
            found=True,
            sam_account_name=(
                item.get(
                    "sam_account_name"
                )
            ),
            email=email or None,
            is_disabled=item.get(
                "is_disabled"
            ),
        )

    return RelatedAccountSearchResult(
        search_key=normalized_search_key,
        found=False,
        sam_account_name=None,
        email=None,
        is_disabled=None,
    )


def discover_related_accounts(
    username: str,
) -> list:
    search_keys = generate_search_keys(
        username
    )

    results = []

    for search_key in search_keys:
        result = search_related_account(
            search_key
        )

        results.append(
            result
        )

    return results


def build_offboarding_request(
    related_account: RelatedAccountSearchResult,
) -> EmployeeOffboardingApiRequest:

    return EmployeeOffboardingApiRequest(
        employee_id="",

        email=related_account.email,

        reason="resigned",

        effective_time=generate_effective_time(),
    )

def discover_users_and_build_requests(
    users: list[RaSoatOffboardingSourceUser],
) -> tuple[
    list[EmployeeOffboardingApiRequest],
    list[RelatedAccountSearchResult],
]:

    requests = []
    discovery_results = []

    total_users = len(users)

    for index, user in enumerate(
        users,
        start=1,
    ):
        print(
            f"[{index}/{total_users}] "
            f"Discovering related accounts for "
            f"{user.username}"
        )

        related_accounts = (
            discover_related_accounts(
                user.username
            )
        )

        discovery_results.extend(
            related_accounts
        )

        for related_account in related_accounts:

            if not related_account.found:
                print(
                    "  NOT FOUND: "
                    f"{related_account.search_key}"
                )
                continue

            if related_account.is_disabled is True:
                print(
                    "  ALREADY DISABLED: "
                    f"{related_account.sam_account_name}"
                )
                continue

            if related_account.is_disabled is None:
                print(
                    "  SKIP: cannot determine "
                    "account status: "
                    f"{related_account.sam_account_name}"
                )
                continue

            if not related_account.email:
                print(
                    "  SKIP: active account found "
                    "but email is empty: "
                    f"{related_account.search_key}"
                )
                continue

            request = build_offboarding_request(
                related_account
            )

            requests.append(
                request
            )

            print(
                "  REQUEST READY: "
                f"{related_account.email}"
            )

    return (
        requests,
        discovery_results,
    )