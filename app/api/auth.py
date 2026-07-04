import bcrypt

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends

from app.auth.fake_users import users

from app.auth.jwt_handler import (
    create_access_token
)

from app.auth.dependencies import (
    get_current_user
)

print("AUTH V2 LOADED")
router = APIRouter()


@router.post("/login")
def login(data: dict):

    username = data["username"]
    password = data["password"]

    user = users.get(username)

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credential"
        )

    if not bcrypt.checkpw(
        password.encode(),
        user["password_hash"].encode()
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credential"
        )

    token = create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def me(
    current_user=Depends(
        get_current_user
    )
):

    return current_user