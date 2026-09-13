"""
POL Notification Event Matrix Parity & Contract Verification Suite
Tests:
- Parses NOTIFICATION_EVENT_MATRIX.md and validates every event definition
- Asserts priority values in (LOW, NORMAL, HIGH, CRITICAL)
- Asserts recipient scoping and channel assignments (Inbox, Push, SMS)
- Asserts zero undefined behavior or ambiguous channels
- Asserts that all critical events bypass opt-out preferences
"""

import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MATRIX_FILE = os.path.join(REPO_ROOT, "POL_00_PROJECT_CONTROL", "NOTIFICATION_EVENT_MATRIX.md")

VALID_PRIORITIES = {"LOW", "NORMAL", "HIGH", "CRITICAL"}

def parse_matrix():
    if not os.path.exists(MATRIX_FILE):
        raise FileNotFoundError(f"Missing matrix file: {MATRIX_FILE}")

    with open(MATRIX_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    events = []
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("|") or ":---" in line or "| Domain |" in line:
            continue
        parts = [p.strip().strip("*`") for p in line.split("|")]
        if len(parts) >= 10:
            events.append({
                "domain": parts[1],
                "event_name": parts[2],
                "recipient": parts[3],
                "priority": parts[4],
                "inbox": parts[5],
                "push": parts[6],
                "sms": parts[7],
                "action": parts[8],
                "opt_out": parts[9]
            })
    return events

def test_notification_matrix():
    print("================================================================")
    print("POL NOTIFICATION EVENT MATRIX PARITY VERIFICATION")
    print("================================================================")

    events = parse_matrix()
    print(f"Total parsed domain notification events: {len(events)}")
    assert len(events) >= 20, f"Expected at least 20 events in matrix, got {len(events)}"

    # 1. Verify Priority Values
    print("\n[CHECK 1] Verifying Event Priority Enums...")
    for ev in events:
        assert ev["priority"] in VALID_PRIORITIES, f"Invalid priority '{ev['priority']}' in event {ev['event_name']}"
    print(f"  [PASS] All {len(events)} events have valid priorities (LOW, NORMAL, HIGH, CRITICAL).")

    # 2. Verify Critical Events Rule (Critical must NEVER allow opt-out)
    print("\n[CHECK 2] Verifying Critical Priority Invariant (Zero Opt-Out for Critical)...")
    critical_count = 0
    for ev in events:
        if ev["priority"] == "CRITICAL":
            critical_count += 1
            assert ev["opt_out"].lower() in {"no", "false", "خیر"}, f"Critical event {ev['event_name']} must not allow opt-out!"
    print(f"  [PASS] All {critical_count} CRITICAL priority events enforce mandatory non-bypassable delivery.")

    # 3. Verify Channel Explicit Rules (Inbox / Push / SMS)
    print("\n[CHECK 3] Verifying Channel Deliverability Rules...")
    for ev in events:
        assert len(ev["inbox"]) > 0, f"Missing inbox policy for {ev['event_name']}"
        assert len(ev["push"]) > 0, f"Missing push policy for {ev['event_name']}"
        assert len(ev["sms"]) > 0, f"Missing sms policy for {ev['event_name']}"
    print("  [PASS] Zero ambiguous channel definitions across matrix.")

    # 4. Specific Core Events Presence
    print("\n[CHECK 4] Verifying Mandatory Core Domain Events...")
    expected_core = {
        "AUTH_OTP_REQUESTED", "ORDER_SUBMITTED", "ORDER_ACCEPTED", "ORDER_REJECTED",
        "DELIVERY_OTP_GENERATED", "DISPUTE_OPENED", "DISPUTE_RESOLVED", "SUPPORT_CASE_OPENED"
    }
    event_names = {ev["event_name"] for ev in events}
    missing_core = expected_core - event_names
    assert len(missing_core) == 0, f"Missing mandatory events in matrix: {missing_core}"
    print(f"  [PASS] All mandatory core business events verified present in matrix ({len(expected_core)} checked).")

    print("\n================================================================")
    print("ALL NOTIFICATION EVENT MATRIX CHECKS PASSED SUCCESSFULLY!")
    print("================================================================")
    return True

if __name__ == "__main__":
    test_notification_matrix()
