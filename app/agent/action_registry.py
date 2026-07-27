ACTION_REGISTRY = {
    "disable_user": {
        "display_name": "Disable AD User",

        "description": (
            "Disable or lock an Active Directory user account"
        ),

        "intent_hints": [
            "disable user",
            "disable account",
            "lock user",
            "lock account",
            "khóa user",
            "khoa user",
            "khóa tài khoản",
            "khoa tai khoan",
            "vô hiệu hóa user",
            "vo hieu hoa user",
            "disable"
        ],

        "required_objects": [
            {
                "object_type": "USER",
                "search_tool": "search_user",
                "required": True,
                "action_param": "sam_account_name"
            }
        ],

        "action_tool": "disable_user",

        "action_api": "/api/ad/disable-user",

        "required_action_group": "ad_dis_user",

        "confirm_required": True
    },

    "add_group_member": {
        "display_name": "Add User To Group",

        "description": (
            "Add an Active Directory user to a group"
        ),

        "intent_hints": [
            "add ... group",
            "add to group",
            "add user to group",
            "add member",
            "thêm group",
            "them group",
            "thêm vào nhóm",
            "them vao nhom",
            "add vào nhóm",
            "add vao nhom",
            "cho vào nhóm",
            "cho vao nhom"
        ],

        "required_objects": [
            {
                "object_type": "USER",
                "search_tool": "search_user",
                "required": True,
                "action_param": "sam_account_name"
            },
            {
                "object_type": "GROUP",
                "search_tool": "search_group",
                "required": True,
                "action_param": "group_name"
            }
        ],

        "action_tool": "add_group_member",

        "action_api": "/api/ad/add-group",

        "required_action_group": "ad_add_group",

        "confirm_required": True
    },

    "remove_group_member": {
        "display_name": "Remove User From Group",

        "description": (
            "Remove an Active Directory user from a group"
        ),

        "intent_hints": [
            "remove... group",
            "remove from group",
            "remove user from group",
            "remove member",
            "gỡ user... group",
            "gỡ tài khoản... group",
            "gỡ khỏi nhóm",
            "go khoi nhom",
            "xoá khỏi nhóm",
            "xoa khoi nhom",
            "xóa khỏi nhóm",
            "remove khỏi nhóm",
            "remove khoi nhom"
        ],

        "required_objects": [
            {
                "object_type": "USER",
                "search_tool": "search_user",
                "required": True,
                "action_param": "sam_account_name"
            },
            {
                "object_type": "GROUP",
                "search_tool": "search_group",
                "required": True,
                "action_param": "group_name"
            }
        ],

        "action_tool": "remove_group_member",

        "action_api": "/api/ad/remove-group",

        "required_action_group": "ad_remove_group",

        "confirm_required": True
    },

    "move_user_to_ou": {
        "display_name": "Move User To OU",

        "description": (
            "Move an Active Directory user to another OU"
        ),

        "intent_hints": [
            "move user",
            "move to ou",
            "move user to ou",
            "move account",
            "chuyển user",
            "chuyen user",
            "chuyển tài khoản",
            "chuyen tai khoan",
            "chuyển sang ou",
            "chuyen sang ou",
            "move sang ou",
            "đưa user sang",
            "dua user sang"
        ],

        "required_objects": [
            {
                "object_type": "USER",
                "search_tool": "search_user",
                "required": True,
                "action_param": "sam_account_name"
            },
            {
                "object_type": "OU",
                "search_tool": "search_ou",
                "required": True,
                "action_param": "target_ou_dn"
            }
        ],

        "action_tool": "move_user_to_ou",

        "action_api": "/api/ad/move-user",

        "required_action_group": "ad_move_ou",

        "confirm_required": True
    }
}


SUPPORTED_ACTIONS = list(
    ACTION_REGISTRY.keys()
)