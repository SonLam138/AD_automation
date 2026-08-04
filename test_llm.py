from app.adapters.ldap_adapter import (
    LDAPAdapter
)

# from app.agent.response_planner import (
#     generate_user_response
# )

from app.agent.llm_client import ask_llm

from app.agent.action_prompt import build_action_detection_prompt
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
    "Tôi cần đổi mô tả SonNM thành Nguyen Minh Son"
]

# prompt = build_action_detection_prompt(
#     test_inputs
#     )

for text in test_inputs:

    print("=" * 80)
    print("INPUT =", text)

    resolver_result = resolve_action(
        text,
        ldap.connection
    )

    #Test riêng action dectect, cần tắt cả ldap
    # resolver_result = ask_llm(
    # prompt
    # )


    print("RESOLVER")
    print(resolver_result)
    print()

    # print("COPILOT RESPONSE")

    # response = generate_user_response(
    #     resolver_result
    # )

    # print(response)

    # print()
