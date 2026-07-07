from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

import jwt

from app.auth.jwt_handler import (
    SECRET_KEY,
    ALGORITHM
)

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    print("TOKEN =", credentials.credentials)
    try:

        token = credentials.credentials
        print("TOKEN =", token)
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("PAYLOAD =", payload)
        return payload

    
    except Exception as e:

        print("JWT ERROR =", repr(e))

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
