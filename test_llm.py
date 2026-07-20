from app.adapters.ldap_adapter import (
    LDAPAdapter
)

from app.agent.response_planner import (
    generate_user_response
)

from app.config import (
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)

from app.agent import (
    resolve_action
)


ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)


test_inputs = [
    "Disable tài khoản Minh Son",
    "Thêm tài khoản Test vào group Administrators",
    "chuyển Sonnm sang OU HO",
    "kiểm tra giúp tôi anh Sơn"
]



for text in test_inputs:

    print("=" * 80)
    print("INPUT =", text)

    resolver_result = resolve_action(
        text,
        ldap.connection
    )

    print("RESOLVER")
    print(resolver_result)

    print()

    print("COPILOT RESPONSE")

    response = generate_user_response(
        resolver_result
    )

    print(response)

    print()
