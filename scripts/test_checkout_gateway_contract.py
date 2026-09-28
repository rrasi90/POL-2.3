#!/usr/bin/env python3
"""Regression tests for the canonical checkout boundary."""

import ast
from pathlib import Path

from scripts.checkout_gateway import CanonicalCheckoutGateway

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def test_gateway_delegates_only_to_revalidation_service(monkeypatch):
    calls = {}

    class FakeRevalidation:
        @staticmethod
        def revalidate_and_checkout(**kwargs):
            calls.update(kwargs)
            return {"ok": True}

    monkeypatch.setattr("scripts.checkout_gateway.RevalidationCheckoutService", FakeRevalidation)
    monkeypatch.setattr("scripts.checkout_gateway.CanonicalCheckoutGateway._replay_existing", lambda *args, **kwargs: None)
    monkeypatch.setattr("scripts.checkout_gateway.validate_allocation_against_basket", lambda **kwargs: None)

    class FakeCursor:
        def __init__(self):
            self.executed = []

        def execute(self, query, params=None):
            self.executed.append((query, params))

        def fetchone(self):
            return None

    fake_cur = FakeCursor()
    result = CanonicalCheckoutGateway.checkout(
        cur=fake_cur,
        basket_id="basket",
        plan_id="plan",
        retailer_id="retailer",
        idempotency_key="idem",
        address_snapshot={"city": "Ahvaz"},
        vendor_allocations=[{"vendor_id": "vendor-1"}],
    )

    assert result == {"ok": True}
    assert calls["basket_id"] == "basket"
    assert calls["plan_id"] == "plan"
    assert calls["retailer_id"] == "retailer"


def test_non_test_script_callers_do_not_import_legacy_checkout_service():
    """Prevent production-facing script modules from reintroducing the legacy entry point."""
    offenders = []
    allowed_files = {Path(__file__).name, "domain_services.py"}

    for path in SCRIPTS_DIR.glob("*.py"):
        if path.name in allowed_files or path.name == "__init__.py" or path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "scripts.domain_services":
                for alias in node.names:
                    if alias.name == "CheckoutService":
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
            elif isinstance(node, ast.Attribute) and node.attr == "CheckoutService":
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")

    assert offenders == [], (
        "Legacy CheckoutService is forbidden outside domain_services.py and verification tests; "
        f"use CanonicalCheckoutGateway instead. Offenders: {offenders}"
    )


def test_gateway_source_contains_no_legacy_service_reference():
    source = (SCRIPTS_DIR / "checkout_gateway.py").read_text(encoding="utf-8")
    assert "CheckoutService" not in source.replace("RevalidationCheckoutService", "")
    assert "RevalidationCheckoutService" in source
