from fastapi import APIRouter
from fastapi import HTTPException

from Onboard_UI.schemas.auth import (
    LoginRequest
)

from Onboard_UI.schemas.auth import (
    LoginResponse
)

from Onboard_UI.services.auth_service import (
    authenticate_user
)

from app.auth.jwt_handler import (
    create_access_token
)


router = APIRouter()


@router.post("/login")
def login(
    request: LoginRequest
):

    user = authenticate_user(
        request.username,
        request.password
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials or login group denied"
        )

    token = create_access_token(
        {
            "username":
                user["username"],

            "display_name":
                user["display_name"],

            "groups":
                user["groups"]
        }
    )

    return LoginResponse(
        access_token=token,
        landing_page=user["landing_page"]
    )