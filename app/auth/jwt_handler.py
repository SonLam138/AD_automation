import jwt
from datetime import datetime, timedelta

SECRET_KEY = "ad-capability-secret-automation platform"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user):

    payload = {
        "sub": user["username"],
        "name": user["display_name"],
        "groups": user["groups"],

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