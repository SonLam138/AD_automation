import json
from pathlib import Path

WORKFLOW_REGISTRY = []
registry_file = (
    Path(__file__).parent
    / "workflow_registry.json"
)

with open(
    registry_file,
    "r",
    encoding="utf-8"
) as f:

    WORKFLOW_REGISTRY.extend(json.load(f))

def reload_workflow_registry():

    with open(
        registry_file,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    WORKFLOW_REGISTRY.clear()

    WORKFLOW_REGISTRY.extend(data)

    return WORKFLOW_REGISTRY


