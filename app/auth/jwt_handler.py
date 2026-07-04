import jwt
from datetime import datetime, timedelta

SECRET_KEY = "ad-capability-secret"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user):

    payload = {
        "sub": user["username"],
        "name": user["full_name"],
        "role": user["role"],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow()
               + timedelta(
                    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                 )
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )