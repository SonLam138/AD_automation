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

    "operator01": {
        "username": "operator01",
        "full_name": "AD Operator",
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