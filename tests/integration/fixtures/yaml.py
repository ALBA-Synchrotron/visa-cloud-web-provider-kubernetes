
from pathlib import Path
from typing import Any

import yaml


YAML_DIR = Path("tests/integration/k8s_fixtures/").resolve()


def load_yaml_resources(
        path: str | Path = YAML_DIR,
        *,
        kind: str | None = None,
) -> list[dict[str, Any]]:
    """Load Kubernetes resources from a YAML file or directory."""
    path = Path(path)

    if path.is_dir():
        files = sorted({
            *path.glob("*.yaml"),
            *path.glob("*.yml"),
        })
    elif path.is_file():
        files = [path]
    else:
        raise FileNotFoundError(f"YAML path not found: {path}")

    resources = []

    for yaml_file in files:
        with yaml_file.open(encoding="utf-8") as file:
            for resource in yaml.safe_load_all(file):
                if not isinstance(resource, dict):
                    continue

                if kind is not None and resource.get("kind") != kind:
                    continue

                resources.append(resource)

    return resources
