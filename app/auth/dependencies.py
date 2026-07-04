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

    try:

        token = credentials.credentials

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )