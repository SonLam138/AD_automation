INTEGRATION_CLIENTS = {

    "portal": {

        "display_name":
            "TTVH Portal",

        "client_secret":
            "portal-secret-2026",

        "allowed_endpoints": [

            "some_endpoint",

        ],

        "enabled": False,
    },

    "mail-platform": {

        "display_name":
            "Mail Platform",

        "client_secret":
            "mail-platform-secret-2026",

        "allowed_endpoints": [

            "create_object",

            "disable_object",

            "enable_object",

            "basic_attribute",

            "group_member_add",

            "group_member_remove",

            "move_to_ou",
        ],

        "enabled": True,
    }
}
    