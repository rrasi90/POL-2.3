#!/usr/bin/env python3
"""
POL Master Verification Suite Runner & Machine-Readable Artifact Generator
Executes the full test suite against PostgreSQL 18 and produces:
artifacts/pol-test-results.json
"""

import os
import sys
import json
import time
import datetime
import subprocess
import pytest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.migration_runner import get_connection

class PytestResultCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or (report.when == "setup" and report.failed):
            self.reports.append({
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration": round(report.duration, 4),
                "phase": report.when,
            })

def get_git_info():
    info = {"commit": "unknown", "branch": "unknown", "is_dirty": False}
    try:
        info["commit"] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception:
        info["commit"] = os.environ.get("GITHUB_SHA", "unknown")

    try:
        info["branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception:
        info["branch"] = os.environ.get("GITHUB_REF_NAME", "unknown")

    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
        ).strip()
        info["is_dirty"] = len(status) > 0
    except Exception:
        pass

    return info

def get_db_info():
    try:
        conn, port = get_connection("pol_test")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.execute("""
            SELECT count(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """)
        table_count = cur.fetchone()[0]
        conn.close()
        return {
            "connected": True,
            "port": port,
            "version": version,
            "table_count": table_count,
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }

def run():
    print("=" * 80)
    print("POL INDEPENDENT VERIFICATION & CERTIFICATION TEST SUITE")
    print("=" * 80)

    git_info = get_git_info()
    db_info = get_db_info()

    print(f"Git Commit:   {git_info['commit']}")
    print(f"Git Branch:   {git_info['branch']} (Dirty: {git_info['is_dirty']})")
    print(f"Python Ver:   {sys.version.split()[0]}")
    if db_info.get("connected"):
        print(f"Database:     PostgreSQL on port {db_info['port']} (Tables: {db_info['table_count']})")
        print(f"DB Version:   {db_info['version'].split(',')[0]}")
    else:
        print(f"Database:     FAILED ({db_info.get('error')})")
    print("=" * 80)

    collector = PytestResultCollector()
    start_time = time.time()

    # Run pytest
    pytest_args = [
        "-v",
        "--tb=short",
        os.path.join(REPO_ROOT, "scripts"),
    ]
    exit_code = pytest.main(pytest_args, plugins=[collector])
    duration = round(time.time() - start_time, 2)

    passed = sum(1 for r in collector.reports if r["outcome"] == "passed")
    failed = sum(1 for r in collector.reports if r["outcome"] == "failed")
    skipped = sum(1 for r in collector.reports if r["outcome"] == "skipped")

    overall_status = "PASSED" if (exit_code == 0 and failed == 0) else "FAILED"

    # Assemble JSON document
    results_payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "environment": "CI" if os.environ.get("CI") == "true" else "LOCAL",
            "git": git_info,
            "python": {
                "version": sys.version,
                "executable": sys.executable,
            },
            "postgresql": db_info,
        },
        "summary": {
            "overall_status": overall_status,
            "exit_code": int(exit_code),
            "total_collected": collector.collected,
            "total_passed": passed,
            "total_failed": failed,
            "total_skipped": skipped,
            "duration_seconds": duration,
        },
        "tests": collector.reports,
    }

    # Save to artifacts/pol-test-results.json
    artifacts_dir = os.path.join(REPO_ROOT, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    results_file = os.path.join(artifacts_dir, "pol-test-results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"VERIFICATION SUMMARY: {overall_status}")
    print(f"Total: {collector.collected} | Passed: {passed} | Failed: {failed} | Skipped: {skipped} in {duration}s")
    print(f"Machine-readable artifact written to: {results_file}")
    print("=" * 80)

    return exit_code

if __name__ == "__main__":
    code = run()
    sys.exit(code)
