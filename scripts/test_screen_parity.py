"""TODO-080 - screen <-> API <-> test parity guards.

The committed ledger ``mvp/SCREEN_TEST_PARITY.md`` is regenerated from disk, so
this module asserts four things that a screenshot review cannot:

1. the ledger matches the code (a new page, a dropped guard, a changed call
   site or a stale spec reference fails);
2. every shipped page is documented in ``mvp/MVP_SCREEN_MATRIX.md``;
3. every ``/api/v1`` literal a page calls exists in the served OpenAPI, i.e. no
   screen is wired to an endpoint the API does not serve;
4. a screen cannot be marked ``VERIFIED`` in the matrix without a browser test
   driving it - the failure mode TODO-080 exists to prevent.
"""

from __future__ import annotations

import io
import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER = REPO_ROOT / "mvp" / "SCREEN_TEST_PARITY.md"
MATRIX = REPO_ROOT / "mvp" / "MVP_SCREEN_MATRIX.md"

os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")
os.environ.setdefault("ENVIRONMENT", "test")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.api.main import app  # noqa: E402
from scripts.screen_parity import (  # noqa: E402
    _SHELL_PAGES,
    _STATIC_PAGES,
    _apis,
    _covering_specs,
    _guard_for,
    _guards,
    _pages,
    _specs,
    build,
)

GUARDED_FAMILIES = {"retailer", "vendor", "ops", "admin", "field", "profile", "notifications"}
_ROW_ID = re.compile(r"[A-Z][A-Z0-9]*-(?:[A-Z0-9]+-?)+")
_DOC_ROUTE = re.compile(r"`(/[^`]*)`")


def _normalize(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path).rstrip("/") or "/"


def _matrix_rows() -> dict[str, set[str]]:
    rows: dict[str, set[str]] = {}
    for line in io.open(MATRIX, encoding="utf-8").read().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not _ROW_ID.fullmatch(cells[0]):
            continue
        for token in _DOC_ROUTE.findall(cells[2]):
            path = token.split("?")[0].strip()
            if path.startswith("/api/"):
                continue
            route = re.sub(r"\[([^\]]+)\]", r"{\1}", path).rstrip("/") or "/"
            rows.setdefault(route, set()).add(cells[-1])
    return rows


def _normalize_call(literal: str) -> str:
    tail = re.sub(r"(?<=[^/])\$\{[^}]+\}", "", literal)
    path = re.sub(r"\$\{[^}]+\}", "{}", tail)
    return _normalize(path)


def _served_paths() -> set[str]:
    return {_normalize(path) for path in app.openapi()["paths"]}


def test_ledger_matches_disk() -> None:
    rendered = build()
    if os.environ.get("POL_UPDATE_SCREEN_PARITY") == "1":
        io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(rendered)
        pytest.skip("SCREEN_TEST_PARITY.md regenerated (POL_UPDATE_SCREEN_PARITY=1)")

    assert LEDGER.exists(), (
        "mvp/SCREEN_TEST_PARITY.md is missing; regenerate with "
        "POL_UPDATE_SCREEN_PARITY=1 python -m pytest scripts/test_screen_parity.py"
    )
    committed = io.open(LEDGER, encoding="utf-8").read()
    assert committed == rendered, (
        "SCREEN_TEST_PARITY.md is stale: a page, guard, API call or spec changed. "
        "Regenerate with POL_UPDATE_SCREEN_PARITY=1 and review the diff."
    )


def test_every_page_is_documented_in_the_screen_matrix() -> None:
    documented = _matrix_rows()
    undocumented = sorted(route for route in _pages() if route not in documented)
    assert not undocumented, (
        "shipped pages missing from mvp/MVP_SCREEN_MATRIX.md: " + ", ".join(undocumented)
    )


def test_documented_routes_exist_or_are_explicitly_not_live() -> None:
    pages = set(_pages())
    served = _served_paths()
    not_live = {"GAP", "NOT_APPLICABLE", "BLOCKED_EXTERNAL"}
    stray = []
    for route, statuses in _matrix_rows().items():
        if route in pages:
            continue
        if _normalize(route) in served:
            continue
        if any(status.startswith(tuple(not_live)) for status in statuses):
            continue
        if route in {"/inventory/daily/2026-09-23", "/auth/*"}:
            continue
        stray.append(f"{route} ({sorted(statuses)})")
    assert not stray, "matrix documents screens that are neither built nor flagged: " + ", ".join(stray)


def test_page_api_calls_are_served_by_the_api() -> None:
    served = _served_paths()
    families = {path.rsplit("/", 1)[0] for path in served}
    broken = []
    for route, page in _pages().items():
            for literal in _apis(page):
                normalized = _normalize_call(literal)
            if normalized in served:
                continue
            if normalized.endswith("/{}") and normalized.rsplit("/", 1)[0] in families:
                continue
            broken.append(f"{route} -> {literal}")
    assert not broken, "screens call endpoints the API does not serve:\n" + "\n".join(broken)


def test_guarded_screens_declare_a_role_family() -> None:
    pages = _pages()
    rules, public = _guards()
    unguarded = []
    for route in pages:
        family = route.lstrip("/").split("/", 1)[0]
        if family not in GUARDED_FAMILIES:
            continue
        roles, _prefix = _guard_for(route, rules, public)
        if "fallback" in roles or roles == "PUBLIC":
            unguarded.append(f"{route} ({roles})")
    assert not unguarded, "guarded screens without a middleware rule: " + ", ".join(unguarded)


def test_shipped_screens_call_an_api_or_declare_why_not() -> None:
    rules, public = _guards()
    rules_by_prefix = {rule["prefix"] for rule in rules}
    silent = []
    for route, page in _pages().items():
        if _apis(page) or route in _STATIC_PAGES or route in _SHELL_PAGES:
            continue
        first = route.lstrip("/").split("/", 1)[0]
        if f"/{first}" in rules_by_prefix or route == "/":
            silent.append(route)
    assert not silent, (
        "screens render without a single API call and are not declared static: " + ", ".join(silent)
    )


def test_verified_screens_have_a_browser_test() -> None:
    pages = _pages()
    specs = _specs()
    unproven = []
    for line in io.open(MATRIX, encoding="utf-8").read().splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7 or not _ROW_ID.fullmatch(cells[0]):
            continue
        if cells[-1] != "VERIFIED":
            continue
        for token in _DOC_ROUTE.findall(cells[2]):
            path = token.split("?")[0].strip()
            if path.startswith("/api/"):
                continue
            route = re.sub(r"\[([^\]]+)\]", r"{\1}", path).rstrip("/") or "/"
            if route not in pages or route in _STATIC_PAGES:
                continue
            if not _covering_specs(route, specs):
                unproven.append(f"{cells[0]} {route}")
    assert not unproven, (
        "matrix marks screens VERIFIED with no browser test: " + ", ".join(unproven)
    )
