ACTION_MAPPING = {

    (
        "CREATE_NEW_USER",
        "CREATE"
    ):
        "create_user",

    (
        "CREATE_NEW_GROUP",
        "CREATE"
    ):
        "create_group",

    (
        "USER",
        "DISABLE"
    ):
        "disable_user",

    (
        "USER",
        "MOVE"
    ):
        "move_user_to_ou",

    (
        "USER",
        "ADD_GROUP"
    ):
        "add_group_by_dn",

    (
        "USER",
        "REMOVE_GROUP"
    ):
        "remove_group_by_dn",

    (
        "GROUP",
        "MOVE"
    ):
        "move_group_to_ou",

    (
        "COMPUTER",
        "DISABLE"
    ):
        "disable_computer",

    (
        "COMPUTER",
        "MOVE"
    ):
        "move_computer_to_ou"
}

def resolve_action_code(
    object_type: str,
    action: str
):
    return ACTION_MAPPING.get(
        (
            object_type,
            action
        )
    )