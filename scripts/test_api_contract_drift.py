"""TODO-135 - OpenAPI/client contract drift guards.

Three independent drift directions are checked:

1. Runtime OpenAPI vs a committed fingerprint - an endpoint, method, status code,
   request schema (properties/required/enum) or query parameter that changes
   without regenerating the snapshot fails the suite.
2. ``mvp/MVP_API_MAP.md`` rows vs the runtime OpenAPI - the human contract map
   cannot silently reference a route that does not exist.
3. Client call sites (web + mobile ``/api/v1/...`` literals) vs the runtime
   OpenAPI - a screen cannot call a path the API does not serve.

The snapshot is intentionally reviewed and committed: regenerating it is a
contract decision, not a test-run side effect.
"""

from __future__ import annotations

import glob
import io
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = Path(__file__).resolve().parent / "api" / "openapi_contract_snapshot.json"
API_MAP_PATH = REPO_ROOT / "mvp" / "MVP_API_MAP.md"
CLIENT_GLOBS = (
    "mvp/apps/web/src/**/*.ts",
    "mvp/apps/web/src/**/*.tsx",
    "mvp/apps/mobile/src/**/*.ts",
    "mvp/apps/mobile/src/**/*.tsx",
)
API_PREFIX = "/api/v1"

os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")
os.environ.setdefault("ENVIRONMENT", "test")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.api.main import app  # noqa: E402


def _ref_name(schema: dict) -> str | None:
    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
        return ref.rsplit("/", 1)[-1]
    return None


def _describe_schema(spec: dict, schema: dict) -> dict:
    name = _ref_name(schema)
    if not name:
        return {"inline": sorted(schema.keys())}
    component = spec.get("components", {}).get("schemas", {}).get(name, {})
    props = component.get("properties", {}) or {}
    enum_shape: dict[str, list] = {}
    for prop, definition in props.items():
        if isinstance(definition, dict) and isinstance(definition.get("enum"), list):
            enum_shape[prop] = definition["enum"]
    return {
        "ref": name,
        "required": sorted(component.get("required", []) or []),
        "properties": sorted(props.keys()),
        "enums": enum_shape,
    }


def fingerprint() -> dict:
    spec = app.openapi()
    result: dict[str, dict] = {}
    for path, operations in spec.get("paths", {}).items():
        path_entry: dict[str, dict] = {}
        for method, operation in operations.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            params = operation.get("parameters", []) or []
            body = operation.get("requestBody") or {}
            body_schema = (
                body.get("content", {}).get("application/json", {}).get("schema", {}) or {}
            )
            path_entry[method.lower()] = {
                "responses": sorted(operation.get("responses", {}).keys()),
                "query_params": sorted(
                    [param.get("name"), bool(param.get("required"))]
                    for param in params
                    if param.get("in") == "query"
                ),
                "request_body_required": bool(body.get("required")),
                "request_body": _describe_schema(spec, body_schema) if body_schema else None,
            }
        result[path] = path_entry
    return dict(sorted(result.items()))


def _normalize_openapi_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path).rstrip("/") or "/"


def _snapshot_text(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def test_openapi_fingerprint_matches_committed_snapshot() -> None:
    current = fingerprint()
    rendered = _snapshot_text(current)

    if os.environ.get("POL_UPDATE_OPENAPI_SNAPSHOT") == "1":
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        io.open(SNAPSHOT_PATH, "w", encoding="utf-8", newline="\n").write(rendered)
        pytest.skip("openapi snapshot regenerated (POL_UPDATE_OPENAPI_SNAPSHOT=1)")

    assert SNAPSHOT_PATH.exists(), (
        f"missing contract snapshot {SNAPSHOT_PATH}; generate it with "
        "POL_UPDATE_OPENAPI_SNAPSHOT=1 and review the diff"
    )
    committed = json.loads(io.open(SNAPSHOT_PATH, encoding="utf-8").read())

    removed = sorted(set(committed) - set(current))
    added = sorted(set(current) - set(committed))
    changed = sorted(
        path for path in set(current) & set(committed) if current[path] != committed[path]
    )
    assert not (removed or added or changed), (
        "OpenAPI contract drift detected. If intentional, regenerate and review the "
        f"snapshot. removed={removed} added={added} changed={changed}"
    )


ROOT_TRANSPORT = {"/healthz", "/readyz"}


def _api_map_paths() -> set[tuple[str, str]]:
    text = io.open(API_MAP_PATH, encoding="utf-8").read()
    rows: set[tuple[str, str]] = set()
    for line in text.splitlines():
        match = re.match(
            r"^\|\s*(GET|POST|PUT|PATCH|DELETE)(?:/(GET|POST|PUT|PATCH|DELETE))?\s*\|\s*`([^`]+)`",
            line.strip(),
        )
        if not match:
            continue
        methods = [match.group(1)]
        if match.group(2):
            methods.append(match.group(2))
        raw_path = match.group(3).strip()
        raw_path = raw_path.split("?", 1)[0]

        # Rows may document sub-routes in parentheses, e.g.
        # `/orders/delivery-exceptions/{id}` (+ `/resolve`, `/escalate`).
        subroutes: list[str] = []
        paren = re.search(r"\(([^)]*)\)", raw_path)
        if paren:
            subroutes = re.findall(r"`?/[^`,)]+`?", paren.group(1))
            subroutes = [item.strip("`? ") for item in subroutes]
            raw_path = raw_path[: paren.start()].strip()
        raw_path = raw_path.strip("`? ")

        prefix = "" if raw_path in ROOT_TRANSPORT else API_PREFIX
        targets = [raw_path] + [raw_path.rstrip("/") + sub for sub in subroutes]
        for index, target in enumerate(targets):
            applicable = methods if index > 0 else methods[:1]
            for method in applicable:
                rows.add((method, prefix + target))
    return rows


def test_api_map_rows_exist_in_openapi() -> None:
    rows = _api_map_paths()
    assert len(rows) > 30, f"parsed only {len(rows)} rows from MVP_API_MAP.md"
    spec = app.openapi()["paths"]
    by_path = {
        _normalize_openapi_path(path): {method.upper() for method in operations}
        for path, operations in spec.items()
    }

    missing = sorted(
        f"{method} {_normalize_openapi_path(path)}"
        for method, path in rows
        if method not in by_path.get(_normalize_openapi_path(path), set())
    )
    assert not missing, f"MVP_API_MAP.md documents routes/methods the API does not serve: {missing}"


_LITERAL = re.compile(r"""["'`](/api/v1/[^"'`]*)["'`]""")


def _client_paths() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for pattern in CLIENT_GLOBS:
        for raw in glob.glob(str(REPO_ROOT / pattern), recursive=True):
            text = io.open(raw, encoding="utf-8", errors="ignore").read()
            for match in _LITERAL.findall(text):
                path = match.split("?", 1)[0].split("#", 1)[0]
                if not path or path.endswith("/"):
                    continue
                if "${" in path:
                    if "}${" in path:
                        continue
                    path = re.sub(r"\$\{[^}]+\}", "{}", path)
                if path.endswith("{}") and not path.endswith("/{}"):
                    path = path[: -len("{}")]
                found.append((os.path.relpath(raw, REPO_ROOT).replace(os.sep, "/"), path))
    return found


def test_client_call_sites_resolve_to_openapi_paths() -> None:
    calls = _client_paths()
    assert len(calls) > 40, f"only {len(calls)} client call sites discovered"
    spec_paths = {_normalize_openapi_path(path) for path in app.openapi()["paths"]}
    families = {path.rsplit("/", 1)[0] for path in spec_paths}
    unknown = []
    for source, path in calls:
        normalized = _normalize_openapi_path(path)
        if normalized in spec_paths:
            continue
        # `/orders/{id}/delivery/${action}` dispatches over a fixed transition set;
        # accept the family only when the API serves that exact prefix.
        if normalized.endswith("/{}") and normalized.rsplit("/", 1)[0] in families:
            continue
        unknown.append(f"{source}: {path}")
    assert not unknown, "client call sites missing from OpenAPI:\n" + "\n".join(sorted(set(unknown)))
