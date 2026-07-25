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
from app.agent.action_prompt import build_action_detection_prompt

ldap = LDAPAdapter()

ldap.connect(
    LDAP_HOST,
    LDAP_USER,
    LDAP_PASSWORD
)


test_inputs = [
    "Disable user nguyentn"
]



for text in test_inputs:

    print("=" * 80)
    print("INPUT =", text)

    resolver_result = resolve_action(
        text,
        ldap.connection
    )
    ngao = build_action_detection_prompt(text)
    print("RESOLVER")
    print(resolver_result)
    print("NGAO")
    print(ngao)
    print()

    # print("COPILOT RESPONSE")

    # response = generate_user_response(
    #     resolver_result
    # )

    # print(response)

    # print()
