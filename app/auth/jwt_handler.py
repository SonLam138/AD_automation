import jwt
from datetime import datetime, timedelta
import uuid

SECRET_KEY = "ad-capability-secret-automation platform"
SERVICE_KEY = "PVcomBank-Automation-Platform-Enterprise-Secret"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
SERVICE_TOKEN_EXPIRE_MINUTES = 120


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

def create_service_token():

    payload = {
        "iss": "ad-automation",

        "sub":
            "ad-automation-service",

        "aud":
            "mail-platform",

        "iat":
            datetime.utcnow(),

        "exp":
            datetime.utcnow()
            + timedelta(
                minutes=
                SERVICE_TOKEN_EXPIRE_MINUTES
            ),

        "jti":
            str(uuid.uuid4())
    }

    return jwt.encode(
        payload,
        SERVICE_KEY,
        algorithm=ALGORITHM
    )

def verify_service_token(
    token: str
):

    return jwt.decode(
        token,

        SERVICE_KEY,

        algorithms=[
            ALGORITHM
        ],

        audience=
            "ad-automation",

        issuer=
            "mail-platform"
    )

def create_integration_token(
    client_id: str
):

    payload = {

        "iss":
            "ad-automation",

        "sub":
            client_id,

        "aud":
            "ad-automation",

        "actor_type":
            "integration",

        "iat":
            datetime.utcnow(),

        "exp":
            datetime.utcnow()
            + timedelta(
                minutes=60
            ),
    }

    return jwt.encode(
        payload,
        SERVICE_KEY,
        algorithm=ALGORITHM
    )

def verify_integration_token(
    token: str
):

    claims = jwt.decode(

        token,

        SERVICE_KEY,

        algorithms=[
            ALGORITHM
        ],

        audience=
            "ad-automation",
    )

    if (
        claims.get(
            "actor_type"
        )
        != "integration"
    ):
        raise Exception(
            "Invalid actor_type"
        )

    return claims