# test_portal_token.py

import requests


def main():

    token_response = requests.post(
        "http://localhost:8000/api/v1/service/integration/token",

        json={
            "client_id":
                "portal",

            "client_secret":
                "portal-secret-2026"
        }
    )

    token = token_response.json()[
        "access_token"
    ]

    headers = {
    "Authorization":
        f"Bearer {token}"
}

    response = requests.post(

        "http://localhost:8000/api/v1/service/integration/employee_offboarding",
        headers=headers,

        json={
        "employee_id": "",
        "email": "ad.auto8@automate.com.vn",
        "reason": "nghỉ việc",
        "start_date": "17-09-2026",
        "is_emergency": False
        }

    )


if __name__ == "__main__":
    main()