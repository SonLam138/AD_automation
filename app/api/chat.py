from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.adapters.ldap_adapter import (
    LDAPAdapter
)

from app.models.ad_tool import (
    AssistantMessageRequest
)

from app.agent.run_agent  import (
    resolve_action
)

from app.auth.rbac import (
    require_group
)

from app.config import (
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)


router = APIRouter()

ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)

@router.post("/message")
def assistant_message(
    request: AssistantMessageRequest,

    current_user=Depends(
        require_group(
            [
                "ad_login"
            ]
        )
    )
):

    try:

        print(
            "LDAP CONNECTED =",
            ldap.connection.bound
        )

        result = resolve_action(
            user_text=request.message,
            ldap_connection=ldap.connection
        )

        return result

    except Exception as ex:

        raise HTTPException(
            status_code=500,
            detail=str(ex)
        )