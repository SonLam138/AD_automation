import requests

from app.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_SECONDS
)


def ask_llm(
    prompt: str
) -> str:
    """
    Call local Ollama model.

    Used by:
    - llm_action_detector.py

    Rule:
    - This function only returns raw LLM text.
    - It does not parse action.
    - It does not call search tools.
    - It does not call action tools.
    """

    url = (
        OLLAMA_BASE_URL.rstrip("/")
        + "/api/generate"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "num_predict": 256
        }
    }

    response = requests.post(
        url,
        json=payload,
        timeout=OLLAMA_TIMEOUT_SECONDS
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "response",
        ""
    )