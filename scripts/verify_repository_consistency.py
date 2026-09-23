"""POL repository consistency verifier.

The previous verifier hard-coded the 001-003 schema and a historical 56-table
baseline. This version treats the migration directory as the schema authority,
checks current canonical contracts, and performs static Python compilation.
"""

from __future__ import annotations

import ast
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]

HIERARCHY_FILES = [
    REPO_ROOT / "POL_00_PROJECT_CONTROL" / "CURRENT_SOURCE_OF_TRUTH.md",
    REPO_ROOT / "06_PRODUCT" / "Order_Lifecycle.md",
    REPO_ROOT / "08_DATA" / "DOMAIN_MODEL.md",
    REPO_ROOT / "08_DATA" / "MULTI_VENDOR_ORDERING_MODEL.md",
]

HIERARCHY_ENTITIES = ("Basket", "AllocationPlan", "OrderGroup", "Order", "OrderItem")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_migration_chain(directory: Path):
    migrations = sorted(
        directory.glob("[0-9][0-9][0-9]_*.sql"),
        key=lambda path: (int(path.name[:3]), path.name),
    )
    if not migrations:
        return migrations, ["No canonical migrations found"]
    numbers = [int(path.name[:3]) for path in migrations]
    expected = list(range(1, numbers[-1] + 1))
    if numbers != expected:
        return migrations, [f"Migration chain has gaps, duplicates or a missing 001: found {numbers}, expected {expected}"]
    return migrations, []


def run_checks() -> bool:
    passed = 0
    failed = 0
    errors: list[str] = []

    def checked_read(path):
        try:
            return read_text(path)
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read {path.relative_to(REPO_ROOT).as_posix()}: {type(exc).__name__}")
            return ""

    print("=" * 80)
    print("POL REPOSITORY CONSISTENCY & ARCHITECTURAL INTEGRITY AUDIT")
    print(f"Repository Root: {REPO_ROOT}")
    print("=" * 80)

    migrations, migration_errors = check_migration_chain(REPO_ROOT / "migrations")
    errors.extend(migration_errors)
    if migration_errors:
        failed += 1
    else:
        print(f"  [PASS] Current migration chain is contiguous: 001..{int(migrations[-1].name[:3]):03d} ({len(migrations)} files).")
        passed += 1

    ddl = "\n".join(checked_read(p) for p in migrations)

    required_tables = {
        "users", "organizations", "organization_memberships", "retailers", "vendors",
        "products", "vendor_products", "vendor_inventory", "vendor_prices",
        "baskets", "basket_items", "allocation_plans", "allocation_items",
        "order_groups", "orders", "order_items", "inventory_reservations",
        "deliveries", "proof_of_delivery", "disputes", "payments", "refunds",
        "returns", "return_items", "return_events", "outbox_events", "notifications",
        "notification_deliveries", "payment_evidence", "payment_reconciliation_cases",
        "payment_reconciliation_attempts",
    }
    missing = [
        t for t in sorted(required_tables)
        if not re.search(rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(t)}\b", ddl, re.I)
    ]
    if missing:
        errors.append(f"Missing canonical tables in migration chain: {missing}")
        print(f"  [FAIL] Missing tables: {missing}")
        failed += 1
    else:
        print(f"  [PASS] {len(required_tables)} canonical runtime tables are represented in the migration chain.")
        passed += 1

    dec_file = REPO_ROOT / "POL_00_PROJECT_CONTROL" / "DECISION_REGISTER.md"
    assumptions_file = REPO_ROOT / "01_RESEARCH" / "Assumptions_and_Hypotheses.md"
    if not dec_file.exists() or not assumptions_file.exists():
        errors.append("Canonical decision files are missing")
        failed += 1
    else:
        dec = checked_read(dec_file)
        assumptions = checked_read(assumptions_file)
        missing_decisions = [f"D-{i:03d}" for i in range(1, 18) if f"D-{i:03d}" not in dec]
        missing_assumption_refs = [f"D-{i:03d}" for i in range(1, 18) if f"D-{i:03d}" not in assumptions]
        if missing_decisions or missing_assumption_refs:
            errors.append(f"Missing decisions: register={missing_decisions}, assumptions={missing_assumption_refs}")
            failed += 1
        else:
            print("  [PASS] D-001..D-017 are present in canonical decision sources.")
            passed += 1

    hierarchy_ok = all(p.exists() for p in HIERARCHY_FILES) and all(
        all(re.search(rf"\b{re.escape(entity)}s?\b", checked_read(p)) for entity in HIERARCHY_ENTITIES)
        for p in HIERARCHY_FILES if p.exists()
    )
    if hierarchy_ok:
        print("  [PASS] Canonical Basket -> AllocationPlan -> OrderGroup -> Order -> OrderItem hierarchy is documented.")
        passed += 1
    else:
        errors.append("Canonical order hierarchy documentation is incomplete")
        failed += 1

    runtime_files = [
        REPO_ROOT / "scripts" / "revalidation_checkout.py",
        REPO_ROOT / "scripts" / "returns_rma.py",
        REPO_ROOT / "scripts" / "canonical_integration_worker.py",
        REPO_ROOT / "scripts" / "payment_reconciliation_worker.py",
    ]
    runtime_text = "\n".join(checked_read(p) for p in runtime_files if p.exists())
    required_guards = {
        "checkout_order_items": "INSERT INTO order_items" in runtime_text,
        "checkout_vendor_grouping": "allocations_by_vendor" in runtime_text,
        "rma_aggregate": "requested_by_item" in runtime_text,
        "rma_two_person_refund": "completed_by_user_id" in runtime_text and "must be performed by a different actor" in runtime_text,
        "outbox_quarantine": "_quarantine_unsupported" in runtime_text and "status='FAILED'" in runtime_text,
        "payment_conflict_guard": "conflicting_match" in runtime_text and "conflicting_trusted_observations" in runtime_text,
    }
    failed_guards = [name for name, ok in required_guards.items() if not ok]
    if failed_guards:
        errors.append(f"Missing runtime bug-fix guard(s): {failed_guards}")
        failed += 1
    else:
        print("  [PASS] All audited runtime bug-fix guards are present in canonical services/workers.")
        passed += 1

    migration_024 = REPO_ROOT / "migrations" / "024_runtime_bug_fixes_and_audit_guards.sql"
    if migration_024.exists() and "outbox_events_status_canonical_check" in checked_read(migration_024):
        print("  [PASS] Migration 024 runtime audit guards are present.")
        passed += 1
    else:
        errors.append("Migration 024 runtime audit guards are missing")
        failed += 1

    python_errors = []
    for path in (REPO_ROOT / "scripts").rglob("*.py"):
        try:
            ast.parse(checked_read(path), filename=str(path))
        except SyntaxError as exc:
            python_errors.append(f"{path.relative_to(REPO_ROOT)}:{exc.lineno}:{exc.offset}: {exc.msg}")
    if python_errors:
        errors.extend(python_errors[:20])
        print(f"  [FAIL] Python syntax errors: {len(python_errors)}")
        failed += 1
    else:
        print("  [PASS] All scripts/*.py files parse successfully.")
        passed += 1

    dataset_file = REPO_ROOT / "Master SKU" / "backup_no_images.json"
    if dataset_file.exists():
        try:
            count = len(json.loads(read_text(dataset_file)))
            print(f"  [PASS] Master SKU dataset is readable ({count:,} records).")
            passed += 1
        except Exception as exc:
            errors.append(f"Master SKU dataset is not valid JSON: {exc}")
            failed += 1
    else:
        errors.append("Master SKU dataset missing")
        failed += 1

    failed = max(failed, len(errors))
    print("\n" + "=" * 80)
    print(f"PASS: {passed} | FAIL: {failed}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f" - {error}")
    print("=" * 80)
    return failed == 0


if __name__ == "__main__":
    raise SystemExit(0 if run_checks() else 1)
