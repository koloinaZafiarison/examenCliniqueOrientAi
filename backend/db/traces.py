import json
from pathlib import Path


def write_trace(trace: dict, path: str = "ml/data/traces_export.csv") -> None:
    """Journal local minimal; remplacer par PostgreSQL en déploiement."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(trace, ensure_ascii=True) + "\n")