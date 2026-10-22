"""Build the API <-> UI <-> test traceability matrix (TODO-017).

Static analysis over:
- the mounted FastAPI surface (`app.openapi()`), which is the real route list;
- `mvp/MVP_API_MAP.md` (contract rows);
- `mvp/MVP_SCREEN_MATRIX.md` (screens and their primary APIs);
- `scripts/test_*.py` (executed HTTP scenarios).

Output: `mvp/API_UI_TRACEABILITY_MATRIX.md` plus a console summary.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("POL_API_DB_NAME", "pol_test")

ROOT = Path(__file__).resolve().parent.parent
API_PREFIX = "/api/v1"

ROUTE_ROW = re.compile(r"^\|\s*([A-Z/]+)\s*\|\s*`([^`]+)`")
TEST_URL = re.compile(r"(f?)([\"'])/api/v1")
CLIENT_CALL = re.compile(r"(?:TestClient\(app\)|client|\bc)\.(get|post|put|patch|delete)\(")
PARAM = re.compile(r"\{[^}/]+\}")
SCREEN_ROW = re.compile(r"^\|\s*([A-Z][A-Z0-9_-]*[A-Z0-9])\s*\|")
INVENTORY_ONLY = {"test_api_boundary_route_inventory.py"}


def real_operations() -> list[tuple[str, str]]:
    sys.path.insert(0, str(ROOT))
    from scripts.api.main import app  # noqa: WPS433 - deferred for env setup

    ops: list[tuple[str, str]] = []
    for path, spec in app.openapi()["paths"].items():
        for method in spec:
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                ops.append((method.upper(), path))
    return sorted(set(ops))


def map_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for line in (ROOT / "mvp" / "MVP_API_MAP.md").read_text(encoding="utf-8").splitlines():
        match = ROUTE_ROW.match(line)
        if not match:
            continue
        methods, raw_path = match.group(1), match.group(2)
        if raw_path in {"/healthz", "/readyz"}:
            path = raw_path
        elif raw_path.startswith("/api/v1"):
            path = raw_path
        else:
            path = f"{API_PREFIX}{raw_path}"
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        note = cells[2] if len(cells) > 2 else ""
        for method in methods.split("/"):
            rows.setdefault(f"{method} {path}", {"note": note, "raw": raw_path})
    return rows


def _route_regex(path: str) -> re.Pattern[str]:
    path = path.split("?")[0].rstrip("/")
    parts = [("[^/]+" if seg.startswith("{") else re.escape(seg)) for seg in path.strip("/").split("/")]
    return re.compile("^/" + "/".join(parts) + "/?$")


def test_coverage() -> list[dict]:
    entries: list[dict] = []
    for file in sorted((ROOT / "scripts").glob("test_*.py")):
        text = file.read_text(encoding="utf-8", errors="ignore")
        if "/api/v1" not in text:
            continue
        starts: list[tuple[int, str, str]] = []
        for match in TEST_URL.finditer(text):
            starts.append((match.end() - len("/api/v1"), match.group(2), ""))
        for const in re.findall(r"^([A-Za-z_]\w*)\s*=\s*[\"']/api/v1[\"']", text, re.M):
            for match in re.finditer(rf"(f?)([\"'])\{{{const}\}}", text):
                starts.append((match.end(), match.group(2), "/api/v1"))
        for start, quote, prefix in starts:
            end = text.find(quote, start)
            if end == -1:
                continue
            url = prefix + text[start:end]
            if "\n" in url or len(url) > 300:
                continue
            url = url.split("?")[0]
            before = text[max(0, start - 400) : start]
            calls = CLIENT_CALL.findall(before)
            if not calls:
                continue
            method = calls[-1].upper()
            func = ""
            fn = re.findall(r"def (test_\w+)", text[:start])
            if fn:
                func = fn[-1]
            entries.append(
                {
                    "file": file.name,
                    "func": func,
                    "method": method,
                    "url": url,
                    "pattern": _route_regex(url),
                }
            )
    return entries


def screen_rows() -> list[dict]:
    rows: list[dict] = []
    section = ""
    for line in (ROOT / "mvp" / "MVP_SCREEN_MATRIX.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        match = SCREEN_ROW.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue
        if cells[0].upper() == "ID" or cells[1].lower().startswith("title"):
            continue
        rows.append(
            {
                "id": cells[0],
                "title": cells[1],
                "route": cells[2],
                "role": cells[3],
                "apis": cells[4],
                "status": cells[6],
                "section": section,
            }
        )
    return rows


def paths_in(cell: str) -> list[str]:
    found = re.findall(r"`(/[^`\s,;]+)`", cell)
    normalized = [f if f.startswith(API_PREFIX) else f"{API_PREFIX}{f}" for f in found]
    return [p.rstrip(".,)*") for p in normalized]


def main() -> int:
    ops = real_operations()
    contract = map_rows()
    tests = test_coverage()
    screens = screen_rows()

    covered: dict[str, list[str]] = {}
    inventory: dict[str, list[str]] = {}
    for method, path in ops:
        regex = _route_regex(path)
        hits = []
        inv = []
        for entry in tests:
            if not regex.match(entry["url"]):
                continue
            if entry["method"] and entry["method"] in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                if entry["method"] != method:
                    continue
            label = f"{entry['file']}::{entry['func']}" if entry["func"] else entry["file"]
            if entry["file"] in INVENTORY_ONLY:
                inv.append(label)
            else:
                hits.append(label)
        covered[f"{method} {path}"] = sorted(set(hits))
        inventory[f"{method} {path}"] = sorted(set(inv))

    screen_links: dict[str, list[str]] = {}
    for screen in screens:
        for raw in paths_in(screen["apis"]):
            for method, path in ops:
                if _route_regex(path).match(raw):
                    screen_links.setdefault(f"{method} {path}", []).append(screen["id"])

    out_lines = [
        "# POL MVP - API / UI / TEST TRACEABILITY MATRIX",
        "",
        "Generated by `scripts/build_api_ui_traceability.py` (TODO-017). Do not hand-edit; re-run the generator.",
        "",
        f"- Mounted FastAPI operations: **{len(ops)}**",
        f"- API_MAP rows matched to a mounted route: **{sum(1 for m, p in ops if f'{m} {p}' in contract)}**",
        f"- Operations with at least one executed HTTP scenario: **{sum(1 for k, v in covered.items() if v)}**",
        f"- Operations referenced by at least one screen: **{sum(1 for k, v in screen_links.items())}**",
        f"- Screen rows parsed: **{len(screens)}**",
        "",
        "Coverage source: URL literals in `scripts/test_*.py` matched against the mounted path template "
        "and the nearest preceding `client.<method>(` call. A hit means a scenario exists in the suite, "
        "not that every branch of the endpoint is asserted.",
        "",
        "| Method | Path | API_MAP | Screens | Executed scenario | Verdict |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for method, path in ops:
        key = f"{method} {path}"
        in_map = key in contract
        screen_ids = sorted(set(screen_links.get(key, [])))
        hits = covered.get(key, [])
        inv = inventory.get(key, [])
        if hits and screen_ids:
            verdict = "TRACED"
        elif hits:
            verdict = "NO_SCREEN"
        elif inv:
            verdict = "INVENTORY_ONLY"
        else:
            verdict = "NO_TEST"
        scenario = (hits or inv or ["-"])[0]
        count = len(hits or inv)
        out_lines.append(
            "| {} | `{}` | {} | {} | {} | {} |".format(
                method,
                path,
                "REAL" if in_map else "UNMAPPED",
                ", ".join(screen_ids) if screen_ids else "-",
                f"`{scenario}`" + (f" (+{count - 1})" if count > 1 else "") if scenario != "-" else "-",
                verdict,
            )
        )

    unmapped_contract = sorted(set(contract) - {f"{m} {p}" for m, p in ops})
    if unmapped_contract:
        out_lines += ["", "## API_MAP rows without a mounted route", ""]
        out_lines += [f"- `{row}` - {contract[row]['note'][:120]}" for row in unmapped_contract]

    no_test = [f"{m} {p}" for m, p in ops if not covered.get(f"{m} {p}") and not inventory.get(f"{m} {p}")]
    inventory_only = [f"{m} {p}" for m, p in ops if not covered.get(f"{m} {p}") and inventory.get(f"{m} {p}")]
    if inventory_only:
        out_lines += ["", "## Operations covered only by the route-inventory test", ""]
        out_lines += [f"- `{row}`" for row in inventory_only]
    if no_test:
        out_lines += ["", "## Operations with no executed scenario at all", ""]
        out_lines += [f"- `{row}`" for row in no_test]

    (ROOT / "mvp" / "API_UI_TRACEABILITY_MATRIX.md").write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    print(f"operations={len(ops)}")
    print(f"traced={sum(1 for m, p in ops if covered.get(f'{m} {p}') and screen_links.get(f'{m} {p}'))}")
    print(f"no_screen={sum(1 for m, p in ops if covered.get(f'{m} {p}') and not screen_links.get(f'{m} {p}'))}")
    print(f"inventory_only={len(inventory_only)}")
    print(f"no_test={len(no_test)}")
    print(f"contract_without_route={len(unmapped_contract)}")
    print(f"screens={len(screens)} screens_without_route={sum(1 for s in screens if not any(_route_regex(p).match(raw) for raw in paths_in(s['apis']) for m, p in ops))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
