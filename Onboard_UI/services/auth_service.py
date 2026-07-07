from datetime import datetime, timedelta
from .ad_service import authenticate_and_get_profile
import jwt
from app.auth.jwt_handler import (
    SECRET_KEY,
    ALGORITHM
)



def authenticate_user(
    username,
    password
):
    print(f"LOGIN USER = {username}")
    user = authenticate_and_get_profile(
        username,
        password
    )
    print("LDAP RESULT =", user)
    if not user:
        return None
    print("GROUPS =", user["groups"])

    if (
        "Onboard_Approve_Login"
        not in user["groups"]
    ):
        return None
    
    print("AUTH SUCCESS")
    return user



def create_access_token(data: dict):

    payload = data.copy()

    payload["exp"] = (
        datetime.utcnow()
        + timedelta(hours=8)
    )

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )