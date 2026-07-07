import bcrypt

users = {
    "sonnm1": {
        "username": "sonnm1",
        "full_name": "Nguyen Minh Son",
        "password_hash": bcrypt.hashpw(
            "123456".encode(),
            bcrypt.gensalt()
        ).decode(),
        "role": "ad.admin"
    },

    "approver": {
        "username": "approver",
        "full_name": "Onboard Approver",
        "password_hash": bcrypt.hashpw(
            "123456".encode(),
            bcrypt.gensalt()
        ).decode(),
        "role": "ad.operator"
    },

    "viewer01": {
        "username": "viewer01",
        "full_name": "Viewer User",
        "password_hash": bcrypt.hashpw(
            "123456".encode(),
            bcrypt.gensalt()
        ).decode(),
        "role": "ad.viewer"
}
}