# Test/test_service_token.py

from app.auth.jwt_handler import (
    create_service_token
)

import jwt


def main():

    token = (
        create_service_token()
    )

    print(token)

    payload = jwt.decode(
        token,

        "ad-capability-secret-automation platform",

        algorithms=["HS256"],

        audience="mail-platform",
    )

    print(payload)


if __name__ == "__main__":
    main()