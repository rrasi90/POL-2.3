"""Canonical MVP E2E contract entrypoint.

The former master E2E mixed legacy domain-service mutations with canonical
checkout. This entrypoint deliberately exercises the canonical application
boundary contract and delegates detailed regression assertions to the dedicated
canonical regression module.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_master_e2e_uses_canonical_checkout_boundary():
    checkout = _read("scripts/checkout_gateway.py")
    boundary = _read("scripts/application_boundary.py")
    revalidation = _read("scripts/revalidation_checkout.py")
    assert "CanonicalCheckoutGateway" in checkout
    assert "RevalidationCheckoutService" in checkout
    assert "CanonicalCheckoutGateway" in boundary
    assert "INSERT INTO order_items" in revalidation
    assert "allocations_by_vendor" in revalidation
    assert "from scripts.domain_services import" not in _read("scripts/test_e2e_mvp_platform.py")


def test_master_e2e_covers_the_high_risk_checkout_invariants():
    regression = _read("scripts/test_canonical_runtime_regressions.py")
    assert "test_checkout_persists_order_items_and_groups_by_vendor" in regression
    assert "test_checkout_idempotency_key_is_bound_to_request_fingerprint" in regression
    assert "test_rma_aggregates_duplicate_order_item_lines" in regression
    assert "test_refund_requires_operational_actor_and_two_person_control" in regression
    assert "test_unknown_outbox_events_leave_pending_queue_and_enter_failed_quarantine" in regression
    assert "test_payment_reconciliation_rejects_conflicting_trusted_evidence" in regression
