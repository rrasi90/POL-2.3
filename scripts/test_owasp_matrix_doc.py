"""TODO-131 - keep the OWASP matrix honest.

Every `file.py::test_name` reference in `mvp/OWASP_API_SECURITY_MATRIX.md` must
resolve to a real test function in this repository. A row that cites a deleted
or renamed test is a false claim, so the build fails instead.
"""

from __future__ import annotations

import ast
import io
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "mvp" / "OWASP_API_SECURITY_MATRIX.md"
INVENTORY = REPO_ROOT / "mvp" / "API_SERVED_INVENTORY.md"
SCRIPTS = REPO_ROOT / "scripts"

REF = re.compile(r"`(test_[A-Za-z0-9_]+\.py)::([A-Za-z0-9_]+)`")


def _doc() -> str:
    return io.open(DOC, encoding="utf-8").read()


def _test_functions(path: Path) -> set[str]:
    tree = ast.parse(io.open(path, encoding="utf-8").read(), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                names.add(node.name)
        if isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            names.add(node.name)
    return names


def test_matrix_lists_all_ten_top10_rows() -> None:
    text = _doc()
    missing = [f"API{i}" for i in range(1, 11) if f"### API{i} " not in text]
    assert not missing, f"OWASP matrix is missing rows: {missing}"


def test_matrix_references_resolve_to_real_tests() -> None:
    text = _doc()
    refs = sorted(set(REF.findall(text)))
    assert len(refs) >= 20, f"only {len(refs)} test references found in the matrix"

    broken = []
    cache: dict[str, set[str]] = {}
    for filename, test_name in refs:
        path = SCRIPTS / filename
        if not path.exists():
            broken.append(f"{filename} (missing file)")
            continue
        if filename not in cache:
            cache[filename] = _test_functions(path)
        if test_name not in cache[filename]:
            broken.append(f"{filename}::{test_name}")

    assert not broken, "OWASP matrix cites tests that do not exist: " + ", ".join(broken)


def test_matrix_links_the_served_inventory() -> None:
    text = _doc()
    assert INVENTORY.exists(), "API_SERVED_INVENTORY.md must exist (TODO-133)"
    assert "API_SERVED_INVENTORY.md" in text
    assert "TODO-131" in text


@pytest.mark.parametrize("risk", ["API4", "API7"])
def test_uncovered_or_na_rows_state_a_reason(risk: str) -> None:
    text = _doc()
    start = text.index(f"### {risk} ")
    end = text.find("### ", start + 1)
    section = text[start:end]
    assert ("TODO-132" in section) or ("RESOURCE_LIMITS.md" in section) or ("Not applicable" in section), (
        f"{risk} must link the closing TODO or explain why it does not apply"
    )
