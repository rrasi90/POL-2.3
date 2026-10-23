"""TODO-080 - screen <-> API <-> test parity ledger.

Every shipped web screen (``app/**/page.tsx``) is enumerated from the file
system and joined with three independent sources:

* the route guard declared in ``src/middleware.ts`` (role that may open it),
* the ``/api/v1`` paths the page actually calls,
* the Playwright specs that drive that route.

The result is committed as ``mvp/SCREEN_TEST_PARITY.md`` and re-derived by
``scripts/test_screen_parity.py`` so a new screen, a dropped guard, a called
API that does not exist, or a screen claimed complete without a test fails the
suite instead of drifting silently.

Regenerate with ``POL_UPDATE_SCREEN_PARITY=1``.
"""

from __future__ import annotations

import glob
import io
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = REPO_ROOT / "mvp" / "apps" / "web" / "src" / "app"
MIDDLEWARE = REPO_ROOT / "mvp" / "apps" / "web" / "src" / "middleware.ts"
SPEC_GLOB = "mvp/apps/web/tests/*.spec.ts"
OUT_PATH = REPO_ROOT / "mvp" / "SCREEN_TEST_PARITY.md"
API_PREFIX = "/api/v1"

os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")
os.environ.setdefault("ENVIRONMENT", "test")

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_SHELL_PAGES = {
    "/admin": "navigation hub; renders cards that link to /admin/users and /admin/orgs",
}

_STATIC_PAGES = {
    "/": "landing page: marketing copy only",
    "/about": "marketing page",
    "/contact": "marketing page",
    "/how": "marketing page",
    "/legal": "static legal copy",
    "/pilot": "marketing page",
    "/retailers": "marketing page",
    "/vendors": "marketing page",
    "/auth/login": "OTP form: calls /auth/request-otp and /auth/verify-otp via the shared client",
    "/dev/components": "internal design gallery, not part of the product surface",
}


def _route_of(page: Path) -> str:
    rel = page.relative_to(APP_DIR).as_posix()
    parts = [p for p in rel.split("/") if p != "page.tsx" and not p.startswith("(")]
    parts = [re.sub(r"\[([^\]]+)\]", r"{\1}", p) for p in parts]
    return "/" + "/".join(parts) if parts else "/"


def _pages() -> dict[str, Path]:
    return {
        _route_of(Path(path)): Path(path)
        for path in sorted(glob.glob(str(APP_DIR / "**" / "page.tsx"), recursive=True))
    }


def _guards() -> tuple[list[dict], list[str]]:
    text = io.open(MIDDLEWARE, encoding="utf-8").read()
    rules = [
        {"prefix": prefix, "roles": re.findall(r'"([^"]+)"', roles)}
        for prefix, roles in re.findall(
            r'\{\s*prefix:\s*"([^"]+)",\s*roles:\s*\[([^\]]*)\]', text
        )
    ]
    public_block = re.search(r"PUBLIC_PREFIXES\s*=\s*\[([^\]]*)\]", text)
    public = re.findall(r'"([^"]+)"', public_block.group(1)) if public_block else []
    return rules, public


def _guard_for(route: str, rules: list[dict], public: list[str]) -> tuple[str, str]:
    if route == "/" or route in public:
        return "PUBLIC", "/"
    for rule in sorted(rules, key=lambda item: -len(item["prefix"])):
        prefix = rule["prefix"]
        if route == prefix or route.startswith(prefix + "/"):
            roles = rule["roles"]
            if roles == ["*"]:
                return "AUTHENTICATED", prefix
            return ", ".join(roles), prefix
    return "AUTHENTICATED (fallback: session required)", ""


def _apis(page: Path) -> list[str]:
    text = io.open(page, encoding="utf-8", errors="ignore").read()
    found = set()
    for literal in re.findall(r"""["'`](/api/v1/[^"'`]*)["'`]""", text):
        found.add(literal.split("?")[0].split("#")[0])
    return sorted(found)


def _route_regex(route: str) -> re.Pattern:
    pattern = re.sub(r"\{[^}]+\}", "[^/]+", route)
    return re.compile(pattern + r"(?:[/?#\"]|$)")


def _specs() -> dict[str, str]:
    return {
        Path(path).name: io.open(path, encoding="utf-8", errors="ignore").read()
        for path in sorted(glob.glob(str(REPO_ROOT / SPEC_GLOB)))
    }


def _covering_specs(route: str, specs: dict[str, str]) -> list[str]:
    regex = _route_regex(route)
    hits = []
    for name, text in specs.items():
        for literal in re.findall(r"""["'`](/[A-Za-z][^"'`]*)["'`]""", text):
            if regex.search(literal.split("?")[0]):
                hits.append(name)
                break
    return sorted(hits)


def build() -> str:
    pages = _pages()
    rules, public = _guards()
    specs = _specs()
    lines = [
        "# POL MVP — Screen / API / test parity",
        "",
        "Generated from `mvp/apps/web/src/app/**/page.tsx`, `src/middleware.ts`, the",
        "`/api/v1` literals inside each page, and `mvp/apps/web/tests/*.spec.ts`.",
        "Regenerate with `POL_UPDATE_SCREEN_PARITY=1 python -m pytest scripts/test_screen_parity.py`.",
        "",
        "`COVERED` = at least one Playwright spec drives the route; `GAP` = shipped with",
        "no browser test; `STATIC` = intentionally API-free page; `SHELL` = navigation-only",
        "hub (reason recorded).",
        "",
        "| Route | Page | Guard (role prefix) | APIs called by the page | Browser specs | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    covered = gaps = static = shell = 0
    for route in sorted(pages):
        page = pages[route]
        roles, prefix = _guard_for(route, rules, public)
        apis = _apis(page)
        specs_hit = _covering_specs(route, specs)
        if specs_hit:
            status = "COVERED"
            covered += 1
        elif route in _SHELL_PAGES:
            status = "SHELL"
            shell += 1
        elif route in _STATIC_PAGES:
            status = "STATIC"
            static += 1
        else:
            status = "GAP"
            gaps += 1
        api_cell = "<br>".join(f"`{path}`" for path in apis) or ("—" if route in _STATIC_PAGES or route in _SHELL_PAGES else "**none**")
        spec_cell = "<br>".join(f"`{name}`" for name in specs_hit) or "—"
        lines.append(
            f"| `{route}` | `{page.relative_to(REPO_ROOT).as_posix()}` | {roles}"
            f"{f' (`{prefix}`)' if prefix and prefix != '/' else ''} | {api_cell} | {spec_cell} | {status} |"
        )
    lines += [
        "",
        f"**Totals:** {len(pages)} routes — {covered} covered, {gaps} gap, {static} static, {shell} shell.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    rendered = build()
    if os.environ.get("POL_UPDATE_SCREEN_PARITY") == "1":
        io.open(OUT_PATH, "w", encoding="utf-8", newline="\n").write(rendered)
        print(f"wrote {OUT_PATH}")
    else:
        print(rendered)
