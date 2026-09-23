"""Guard: every scripts/test_*.py file must be pytest-collectable (>= 1 test).

Stage 08 regression: scripts/test_auth_contract.py held its tests inside
run_tests() closures, so pytest collected 0 items from it and CI ran with a
silent blind spot for the entire auth contract suite. This guard makes that
class of defect structurally impossible to reintroduce: if any test file in
scripts/ stops collecting tests, verification fails loudly.
"""

import glob
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")


def _collected_test_count(path):
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", path],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**os.environ, "POL_JWT_SECRET": os.environ.get(
            "POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")},
    )
    if proc.returncode != 0:
        return None, proc.stdout + proc.stderr
    for line in proc.stdout.splitlines():
        stripped = line.strip()
        if "no tests collected" in stripped:
            return 0, proc.stdout
        if "tests collected" in stripped or "test collected" in stripped:
            try:
                return int(stripped.split()[0]), proc.stdout
            except (ValueError, IndexError):
                break
    return None, proc.stdout + proc.stderr


def test_every_test_file_collects_at_least_one_test():
    test_files = sorted(glob.glob(os.path.join(SCRIPTS_DIR, "test_*.py")))
    assert test_files, "No test files found under scripts/ — guard cannot run"

    blind_spots = []
    for path in test_files:
        count, _output = _collected_test_count(path)
        rel = os.path.relpath(path, REPO_ROOT).replace(os.sep, "/")
        if count is None:
            blind_spots.append(f"{rel} (collection errored)")
        elif count < 1:
            blind_spots.append(f"{rel} (collected {count})")

    assert not blind_spots, (
        "Test files with zero collected tests — CI blind spot detected: "
        + "; ".join(blind_spots)
    )
