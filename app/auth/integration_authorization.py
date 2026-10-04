from fastapi import (
    Depends,
    HTTPException,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
)

from app.auth.dependencies import (
    security,
)

from app.auth.dependencies import (
    require_integration_token,
)

from app.auth.integration_registry import (
    INTEGRATION_CLIENTS,
)


def require_integration_endpoint(
    endpoint_key: str,
):

    def dependency(
        credentials:
            HTTPAuthorizationCredentials
            = Depends(
                security
            )
    ):

        claims = (
            require_integration_token(
                credentials
            )
        )

        client_id = (
            claims.get(
                "sub"
            )
        )

        client = (
            INTEGRATION_CLIENTS.get(
                client_id
            )
        )

        if not client:

            raise HTTPException(
                status_code=403,
                detail=
                    (
                        "Unknown integration "
                        "client"
                    ),
            )

        if not (
            client.get(
                "enabled",
                False,
            )
        ):

            raise HTTPException(
                status_code=403,
                detail=
                    (
                        "Integration client "
                        "is disabled"
                    ),
            )

        allowed_endpoints = (
            client.get(
                "allowed_endpoints",
                [],
            )
        )

        if (
            endpoint_key
            not in
            allowed_endpoints
        ):

            raise HTTPException(
                status_code=403,
                detail=
                    (
                        "Client is not authorized "
                        "for this endpoint"
                    ),
            )

        return claims

    return dependency