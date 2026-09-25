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
