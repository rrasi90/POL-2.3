"""TODO-133 - served-endpoint inventory must match the live OpenAPI document.

`MVP_API_MAP.md` is the curated map (persona/notes). This test keeps the full
machine inventory of every served operation in `mvp/API_SERVED_INVENTORY.md` so
an endpoint cannot be added, removed, renamed, marked deprecated or have its
auth requirement flipped without an explicit, reviewable regeneration.
"""

from __future__ import annotations

import io
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = REPO_ROOT / "mvp" / "API_SERVED_INVENTORY.md"

os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")
os.environ.setdefault("ENVIRONMENT", "test")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.api.main import app  # noqa: E402

METHODS = ("get", "post", "put", "patch", "delete")


def _row(path: str, method: str, operation: dict) -> str:
    security = operation.get("security")
    auth = "no" if security == [] else "yes"
    deprecated = "yes" if operation.get("deprecated") else ""
    summary = (operation.get("summary") or "").replace("|", "/")
    return f"| `{method.upper()}` | `{path}` | {auth} | {deprecated} | {summary} |"


def render_inventory() -> str:
    spec = app.openapi()
    lines = [
        "# POL API — served endpoint inventory",
        "",
        "Auto-generated from `scripts/api/main.py` OpenAPI (TODO-133). Do not hand-edit:",
        "regenerate with `POL_UPDATE_API_INVENTORY=1 pytest scripts/test_api_inventory.py`.",
        "",
        "| Method | Path | Auth | Deprecated | Summary |",
        "| --- | --- | --- | --- | --- |",
    ]
    count = 0
    for path in sorted(spec["paths"]):
        for method in METHODS:
            operation = spec["paths"][path].get(method)
            if not operation:
                continue
            lines.append(_row(path, method, operation))
            count += 1
    lines.extend(["", f"Total operations: {count}", ""])
    return "\n".join(lines)


def test_served_inventory_matches_openapi() -> None:
    rendered = render_inventory()

    if os.environ.get("POL_UPDATE_API_INVENTORY") == "1":
        INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        io.open(INVENTORY_PATH, "w", encoding="utf-8", newline="\n").write(rendered)
        pytest.skip("served inventory regenerated (POL_UPDATE_API_INVENTORY=1)")

    assert INVENTORY_PATH.exists(), (
        "mvp/API_SERVED_INVENTORY.md is missing; regenerate with POL_UPDATE_API_INVENTORY=1"
    )
    committed = io.open(INVENTORY_PATH, encoding="utf-8").read()
    assert committed == rendered, (
        "Served endpoint inventory drifted from the live OpenAPI document. Regenerate with "
        "POL_UPDATE_API_INVENTORY=1 and review the diff."
    )


def test_inventory_has_no_deprecated_operations() -> None:
    spec = app.openapi()
    deprecated = [
        f"{method.upper()} {path}"
        for path, operations in spec["paths"].items()
        for method, operation in operations.items()
        if method in METHODS and operation.get("deprecated")
    ]
    assert not deprecated, f"deprecated operations are still served: {deprecated}"


def test_every_operation_has_a_unique_operation_id_and_summary() -> None:
    spec = app.openapi()
    seen: dict[str, str] = {}
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            if method not in METHODS:
                continue
            op_id = operation.get("operationId")
            assert op_id, f"{method.upper()} {path} has no operationId"
            assert op_id not in seen, f"duplicate operationId {op_id}: {seen[op_id]} and {path}"
            seen[op_id] = path
            assert operation.get("summary"), f"{method.upper()} {path} has no summary"


def test_inventory_covers_every_served_operation() -> None:
    spec = app.openapi()
    served = sum(
        1
        for operations in spec["paths"].values()
        for method in operations
        if method in METHODS
    )
    text = io.open(INVENTORY_PATH, encoding="utf-8").read()
    assert f"Total operations: {served}" in text
    assert served >= 150, f"unexpectedly small API surface: {served} operations"
    assert "| `GET` | `/healthz` |" in text
    assert "| `POST` | `/api/v1/auth/request-otp` |" in text
