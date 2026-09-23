#!/usr/bin/env python3
"""Structural + anti-vibe-coding scan for mvp/ and scripts/ (UTF-8 safe)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    "todo": re.compile(r"\b(TODO|FIXME|HACK|XXX)\b"),
    "mock_words": re.compile(r"\b(mock|fake|stub|dummy)\b", re.I),
    "window_loc_assign": re.compile(r"window\.location\.href\s*="),
    "console_log": re.compile(r"console\.(log|debug)\("),
    "fake_success": re.compile(r"setTimeout\([^)]*success|always succeed|fakeSuccess", re.I),
    "biz_calc_ui": re.compile(r"quantity\s*\*|commission|taxRate|unit_price\s*\*"),
}

SKIP_PARTS = {"node_modules", ".next", ".git", "__pycache__", "dist", "build"}


def scan_file(path: Path) -> dict[str, list[str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    hits: dict[str, list[str]] = {}
    for name, rx in PATTERNS.items():
        found = []
        for i, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                found.append(f"{path.relative_to(ROOT)}:{i}:{line.strip()[:160]}")
        if found:
            hits[name] = found
    return hits


def main() -> int:
    roots = [ROOT / "mvp", ROOT / "scripts"]
    totals: dict[str, list[str]] = {k: [] for k in PATTERNS}
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix not in {".ts", ".tsx", ".js", ".jsx", ".mjs", ".py"}:
                continue
            if any(p in SKIP_PARTS for p in path.parts):
                continue
            for name, lines in scan_file(path).items():
                totals[name].extend(lines)

    for name, lines in totals.items():
        print(f"=== {name} ({len(lines)}) ===")
        for line in lines[:80]:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
