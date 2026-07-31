DETECTOR_ACTION_CATALOG = [

    # ========================================
    # USER
    # ========================================

    {
        "action": "disable_user",
        "intent_hints": [
            "disable user",
            "khóa user"
        ]
    },


    {
        "action": "update_user_displayName",
        "intent_hints": [
            "đổi displayname",
            "update displayname",
            "đổi hiển thị"
        ]
    },

    {
        "action": "update_user_department",
        "intent_hints": [
            "đổi department",
            "update department",
            "đổi phòng ban"
        ]
    },

    {
        "action": "update_user_description",
        "intent_hints": [
            "đổi mô tả",
            "update mô tả",
            "update description"
        ]
    },

    {
        "action": "move_user_to_ou",
        "intent_hints": [
            "chuyển user",
            "move user",
            "đổi OU"
        ]
    },

    # ========================================
    # GROUP
    # ========================================

    {
        "action": "add_user_to_group",
        "intent_hints": [
            "thêm user vào group",
            "add user to group"
        ]
    },

    {
        "action": "remove_user_from_group",
        "intent_hints": [
            "xóa user khỏi group",
            "remove user from group"
        ]
    },

    # ========================================
    # COMPUTER
    # ========================================

    {
        "action": "disable_computer",
        "intent_hints": [
            "disable computer",
            "khóa computer"
        ]
    },

    {
        "action": "enable_computer",
        "intent_hints": [
            "enable computer",
            "mở khóa computer"
        ]
    }
]