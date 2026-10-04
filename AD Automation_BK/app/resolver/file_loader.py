import json
from pathlib import Path


BASE_DIR = Path(__file__).parent


def load_config() -> dict:

    config_path = BASE_DIR / "config.json"

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def load_prompt(version: str) -> str:

    path = (
        BASE_DIR
        / "prompt"
        / f"prompt_{version}.md"
    )

    return path.read_text(
        encoding="utf-8"
    )


def load_guide(version: str) -> str:

    path = (
        BASE_DIR
        / "guide"
        / f"guide_{version}.md"
    )

    return path.read_text(
        encoding="utf-8"
    )



def load_extract_prompt(
    version: str
) -> str:

    path = (
        BASE_DIR
        / "prompt"
        / f"prompt_extract_{version}.md"
    )

    return path.read_text(
        encoding="utf-8"
    )


def load_resolve_prompt(
    version: str
) -> str:

    path = (
        BASE_DIR
        / "prompt"
        / f"prompt_resolve_{version}.md"
    )

    return path.read_text(
        encoding="utf-8"
    )

def load_knowledge(version: str) -> dict:

    path = (
        BASE_DIR
        / "knowledge"
        / f"knowledge_{version}.json"
    )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)
    
if __name__ == "__main__":

    config = load_config()

    print(config)

    print(
        load_prompt(
            config["prompt_version"]
        )[:300]
    )

    print(
        load_guide(
            config["guide_version"]
        )[:300]
    )

    knowledge = load_knowledge(
        config["knowledge_version"]
    )

    print(
        knowledge["metadata"]
    )