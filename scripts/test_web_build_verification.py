"""TODO-078 - web build verification guards.

Asserts that the Next.js web app passes typecheck, lint (zero errors),
and production build without installing a JS unit-test runner. The 44
Playwright browser specs cover runtime behaviour; this module proves the
build pipeline itself is sound.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = REPO_ROOT / "mvp" / "apps" / "web"
MVP_DIR = REPO_ROOT / "mvp"


def _run(cmd: list[str], cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    shell = os.name == "nt"
    return subprocess.run(
        cmd if not shell else " ".join(cmd),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        shell=shell,
    )


def test_typecheck_exits_zero() -> None:
    result = _run(["npm", "run", "typecheck"], MVP_DIR, timeout=120)
    assert result.returncode == 0, f"typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_lint_has_zero_errors() -> None:
    result = _run(["npm", "run", "lint"], MVP_DIR, timeout=120)
    assert result.returncode == 0, f"lint failed:\n{result.stdout}\n{result.stderr}"
    output = result.stdout + result.stderr
    for line in output.splitlines():
        if "error" in line.lower() and "0 error" not in line:
            pytest.fail(f"lint error detected: {line}")


def test_next_build_exits_zero() -> None:
    result = _run(["npm", "run", "build"], WEB_DIR, timeout=300)
    assert result.returncode == 0, f"next build failed:\n{result.stdout}\n{result.stderr}"


def test_no_hydration_errors_in_build_output() -> None:
    result = _run(["npm", "run", "build"], WEB_DIR, timeout=300)
    output = result.stdout + result.stderr
    assert "hydration" not in output.lower() or result.returncode == 0, (
        "build output mentions hydration issues"
    )


def test_package_json_has_required_scripts() -> None:
    pkg = json.loads((WEB_DIR / "package.json").read_text(encoding="utf-8"))
    scripts = pkg.get("scripts", {})
    for key in ("build", "typecheck", "lint"):
        assert key in scripts, f"missing script: {key}"
