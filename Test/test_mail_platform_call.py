import requests

from app.auth.jwt_handler import (
    create_service_token
)


def main():

    token = create_service_token()

    headers = {
        "Authorization":
            f"Bearer {token}"
    }

    response = requests.post(
        "http://localhost:8001/api/v1/actions/execute",

        headers=headers,

        json={
            "request_id": "REQ_123456",

            "action_code":
                "ONPREM_DISABLE_MAILBOX",

            "parameters": {
                "identity": "ad.auto2"
            }
        },

        timeout=60
    )

    print(
        response.status_code
    )

    print(
        response.json()
    )


if __name__ == "__main__":
    main()