from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.auth.rbac import require_group

from app.adapters.ldap_adapter import LDAPAdapter
from app.adapters.ldap_container import (
    ldap,
)
from app.config import (
    LDAP_BASE_DN
)

router = APIRouter()

# ldap = LDAPAdapter()

# ldap.connect(
#     LDAP_HOST,
#     LDAP_USER,
#     LDAP_PASSWORD
# )


@router.get("/{sam_account_name}")
def get_user(

    sam_account_name: str,

    current_user=Depends(
        require_group([
            "Domain Users",
        ])
    )
):

    result = ldap.search_user(
        LDAP_BASE_DN,
        sam_account_name
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = result[0]

    return {
        "found": True,
        "cn": str(user.cn),
        "sam_account_name": str(
            user.sAMAccountName
        ),
        "distinguished_name": str(
            user.distinguishedName
        )
    }