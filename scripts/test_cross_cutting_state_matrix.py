"""Executable governance checks for the cross-cutting action matrix."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX = REPO_ROOT / "mvp" / "CROSS_CUTTING_STATE_ACTION_MATRIX.md"
MOBILE_API = REPO_ROOT / "mvp" / "apps" / "mobile" / "src" / "api.ts"
MOBILE_APP = REPO_ROOT / "mvp" / "apps" / "mobile" / "AppShell.tsx"
MOBILE_ACCOUNT = REPO_ROOT / "mvp" / "apps" / "mobile" / "src" / "screens" / "AccountMobileScreen.tsx"
CHECKOUT_GATEWAY = REPO_ROOT / "scripts" / "checkout_gateway.py"
REVALIDATION = REPO_ROOT / "scripts" / "revalidation_checkout.py"
FULFILLMENT = REPO_ROOT / "scripts" / "fulfillment_service.py"

EXPECTED_IDS = {f"CC-{i:02d}" for i in range(1, 31)}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cross_cutting_matrix_is_complete_and_unique():
    text = _text(MATRIX)
    ids = re.findall(r"\|\s*(CC-\d{2})\s*\|", text)
    assert set(ids) == EXPECTED_IDS
    assert len(ids) == len(set(ids)) == 30
    for required in (
        "Preconditions",
        "Validation",
        "Loading",
        "Success",
        "Empty/No-op",
        "Error",
        "Retry",
        "Timeout",
        "Conflict/Stale",
        "Offline",
        "401",
        "403",
        "Rate limit",
        "Duplicate/Idempotency",
        "Tenant scope",
        "Audit",
        "Notification",
        "Recovery",
        "Accessibility/RTL",
        "Theme",
        "QA evidence",
    ):
        assert required in text


def test_checkout_matrix_is_backed_by_canonical_gate_and_revalidation():
    gateway = _text(CHECKOUT_GATEWAY)
    checkout = _text(REVALIDATION)
    assert "pg_advisory_xact_lock" in gateway
    assert "_replay_existing" in gateway
    assert "checkout_request_fingerprint" in checkout
    assert "INSERT INTO order_items" in checkout
    assert "order_item_id" in checkout
    assert "FOR UPDATE" in checkout


def test_delivery_matrix_is_backed_by_canonical_state_machine():
    service = _text(FULFILLMENT)
    assert "VALID_FULFILLMENT_TRANSITIONS" in service
    assert "VALID_DELIVERY_TRANSITIONS" in service
    assert '"READY": {"DISPATCHED", "CANCELLED"}' in service
    assert '"DISPATCHED": {"DELIVERED"}' in service
    assert "otp_code" in service
    assert "proof_type" in service


def test_mobile_session_rows_match_source_contracts():
    api = _text(MOBILE_API)
    app = _text(MOBILE_APP)
    account = _text(MOBILE_ACCOUNT)
    assert "expo-secure-store" in api
    assert "SecureStore.setItemAsync" in api
    assert "SecureStore.getItemAsync" in api
    assert '"/api/v1/auth/refresh"' in api
    assert '"/api/v1/auth/sessions/current"' in account or '"/api/v1/auth/sessions/current"' in api
    assert "refreshAccessToken" in api
    assert "clearSession" in api
    assert "AUTH_EXPIRED" in api
    assert "401" in _text(MATRIX)
    # Device/runtime persistence remains a separate evidence gate; this test only
    # proves the declared source contract is present and matrix-traceable.
