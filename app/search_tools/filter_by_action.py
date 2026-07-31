def filter_candidates_by_action(
    action: str,
    users: list
):
    if not users:
        return []

    if action == "disable_user":
        return [
            user
            for user in users
            if not user.get("is_disabled", False)
        ]

    if action == "enable_user":
        return [
            user
            for user in users
            if user.get("is_disabled", False)
        ]

    if action == "disable_user":
        return [
            user
            for user in users
            if not user.get("is_disabled", False)
        ]

    return users