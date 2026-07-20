from app.agent.confirm_prompt import (
    build_confirm_prompt
)

from app.agent.llm_client import (
    ask_llm
)


def generate_user_response(
    resolver_result: dict
):

    prompt = build_confirm_prompt(
        resolver_result
    )

    response = ask_llm(
        prompt
    )

    return response.strip()