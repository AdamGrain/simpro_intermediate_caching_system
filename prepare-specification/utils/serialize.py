
import json
from pathlib import Path
from typing import Any

def _to_ruamel(obj: Any) -> Any:
    """Recursively convert plain dicts/lists to ruamel CommentedMap/CommentedSeq.

    ruamel's round-trip dumper requires its own container types to emit
    block-style YAML. Plain Python dicts are dumped as flow-style by default,
    which produces single-line output unsuitable for hand-edited config files.
    """
    from ruamel.yaml.comments import CommentedMap, CommentedSeq
    if isinstance(obj, dict):
        cm = CommentedMap()
        for k, v in obj.items():
            cm[k] = _to_ruamel(v)
        return cm
    if isinstance(obj, list):
        cs = CommentedSeq()
        for item in obj:
            cs.append(_to_ruamel(item))
        return cs
    return obj


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a plain Python dict."""
    from ruamel.yaml import YAML
    yaml = YAML(typ="safe")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.load(fh)


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON file and return its contents as a plain Python dict."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_yaml(data: dict[str, Any], path: str | Path) -> None:
    """Serialise data to a block-style YAML file at path."""
    from ruamel.yaml import YAML
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(sequence=2, offset=0)
    yaml.width = 120
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(_to_ruamel(data), fh)
    print(f"Wrote {path}")
