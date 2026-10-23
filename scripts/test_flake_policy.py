"""TODO-136 - flakiness, test independence and CI failure diagnosability.

Static guards plus the written audit in `mvp/FLAKE_AUDIT.md`. The guards are
deliberately about *policy* (how a failure is surfaced), not about how many
tests exist: a retry must never hide an initial failure, a browser test must
not sleep, and a Python test must not sleep outside the two justifyable spots
listed in the audit.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
WEB_TESTS = REPO_ROOT / "mvp" / "apps" / "web" / "tests"
PLAYWRIGHT_CONFIG = REPO_ROOT / "mvp" / "apps" / "web" / "playwright.config.ts"

SLEEP_ALLOWLIST = {"test_http_live_transport.py", "test_flake_policy.py"}


def _config() -> str:
    return io.open(PLAYWRIGHT_CONFIG, encoding="utf-8").read()


def test_playwright_retries_only_in_ci_and_keep_artifacts_on_failure():
    config = _config()
    assert re.search(r"retries:\s*process\.env\.CI\s*\?\s*1\s*:\s*0", config), (
        "local runs must not retry; CI may retry once and must report the flake"
    )
    for key in ("trace", "screenshot", "video"):
        match = re.search(rf'{key}:\s*"([^"]+)"', config)
        assert match, f"{key} must be configured"
        assert "failure" in match.group(1), f"{key} must be kept on failure ({match.group(1)})"


def test_playwright_declares_explicit_timeouts():
    config = _config()
    assert re.search(r"timeout:\s*\d+_?\d*", config), "test timeout must be explicit"
    assert re.search(r"expect:\s*\{\s*timeout:", config), "expect timeout must be explicit"


def test_browser_tests_do_not_sleep_or_focus_a_single_test():
    offenders = []
    for path in WEB_TESTS.glob("*.spec.ts"):
        source = io.open(path, encoding="utf-8").read()
        if "waitForTimeout(" in source:
            offenders.append(f"{path.name}: waitForTimeout")
        if re.search(r"\btest\.only\(", source):
            offenders.append(f"{path.name}: test.only")
    assert not offenders, "; ".join(offenders)


def test_browser_tests_prefer_role_and_label_locators():
    assert WEB_TESTS.exists(), "web tests directory is missing"
    specs = list(WEB_TESTS.glob("*.spec.ts"))
    assert specs, "no browser specs found"
    total_role = sum(
        io.open(path, encoding="utf-8").read().count("getByRole(") for path in specs
    )
    assert total_role >= 10, f"only {total_role} getByRole locators across the suite"


def test_python_tests_do_not_sleep_outside_the_allowlist():
    offenders = []
    for path in SCRIPTS.glob("test_*.py"):
        if path.name in SLEEP_ALLOWLIST:
            continue
        if "time.sleep(" in io.open(path, encoding="utf-8").read():
            offenders.append(path.name)
    assert not offenders, "unexplained sleep in: " + ", ".join(sorted(offenders))


def test_flake_audit_document_exists_and_records_evidence():
    path = REPO_ROOT / "mvp" / "FLAKE_AUDIT.md"
    assert path.exists(), "mvp/FLAKE_AUDIT.md is required (TODO-136)"
    doc = io.open(path, encoding="utf-8").read()
    for token in ("repeat-each=2", "--workers=1", "TODO-136", "retain-on-failure", "allowlist"):
        assert token in doc, token
