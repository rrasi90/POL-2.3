"""Static/runtime route registration hygiene checks."""

from scripts.api.main import app


def test_http_method_and_path_are_unique():
    seen: dict[tuple[str, str], list[str]] = {}
    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        path = getattr(route, "path", None)
        endpoint = getattr(getattr(route, "endpoint", None), "__name__", repr(getattr(route, "endpoint", None)))
        if not path:
            continue
        for method in methods:
            key = (method.upper(), path)
            seen.setdefault(key, []).append(endpoint)

    duplicates = {key: endpoints for key, endpoints in seen.items() if len(endpoints) > 1}
    assert not duplicates, f"Duplicate HTTP registrations detected: {duplicates}"

import ast
from pathlib import Path


def test_api_layer_does_not_import_legacy_domain_services():
    """Keep FastAPI transport on the application boundary."""
    repo_root = Path(__file__).resolve().parents[1]
    api_root = repo_root / "scripts" / "api"
    offenders = []
    for path in api_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "scripts.domain_services":
                offenders.append(str(path.relative_to(repo_root)))
    assert not offenders, f"API transport imports legacy domain_services directly: {offenders}"


if __name__ == "__main__":
    test_http_method_and_path_are_unique()
    test_api_layer_does_not_import_legacy_domain_services()
