"""Regression contracts for the 2026-09-16 repository-wide bug audit.

These tests are intentionally dependency-light so CI can catch architectural
regressions even when an external PostgreSQL runtime is unavailable.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_checkout_persists_order_items_and_groups_by_vendor():
    src = read("scripts/revalidation_checkout.py")
    assert "allocations_by_vendor" in src
    assert "INSERT INTO order_items" in src
    assert "vendor_total = sum(a[\"amount_toman\"] for a in vendor_allocs)" in src
    assert "f\"res-{idempotency_key}-{alloc['vendor_product_id']}\"" in src


def test_rma_aggregates_duplicate_order_item_lines():
    src = read("scripts/returns_rma.py")
    assert "requested_by_item = {}" in src
    assert "requested_by_item[item_key] = requested_by_item.get(item_key, 0) + quantity" in src
    assert "Aggregated return quantity exceeds delivered/ordered quantity." in src
    assert "uq_return_items_return_order_item" in read("migrations/024_runtime_bug_fixes_and_audit_guards.sql")


def test_refund_requires_operational_actor_and_two_person_control():
    src = read("scripts/returns_rma.py")
    assert "OPS_ROLES" in src
    assert "allowed = ops_ok" in src
    assert "completed_by_user_id=%s" in src
    assert "must be performed by a different actor than the approver" in src


def test_unknown_outbox_events_leave_pending_queue_and_enter_failed_quarantine():
    src = read("scripts/canonical_integration_worker.py")
    assert "_quarantine_unsupported" in src
    assert "status='FAILED'" in src
    migration = read("migrations/024_runtime_bug_fixes_and_audit_guards.sql")
    assert "outbox_events_status_canonical_check" in migration
    assert "'FAILED'" in migration


def test_payment_reconciliation_rejects_conflicting_trusted_evidence():
    src = read("scripts/payment_reconciliation_worker.py")
    assert "conflicting = len(distinct_values) > 1" in src
    assert "conflicting_match = conflicting and matches_expected" in src
    assert "if conflicting_match:" in src
    assert "status='MISMATCH'" in src


def test_repository_verifier_is_dynamic_not_legacy_56_table_audit():
    src = read("scripts/verify_repository_consistency.py")
    assert "glob(\"[0-9][0-9][0-9]_*.sql\")" in src
    assert "Current migration chain is contiguous" in src
    assert "56 Tables" not in src
    assert "migration_file_1" not in src


def test_canonical_e2e_contract_is_present():
    checkout_gateway = read("scripts/checkout_gateway.py")
    boundary = read("scripts/application_boundary.py")
    assert "CanonicalCheckoutGateway" in checkout_gateway
    assert "revalidation_checkout" in checkout_gateway
    assert "CanonicalCheckoutGateway" in boundary
    assert "legacy domain_services" not in boundary.lower()
