"""
POL Canonical Checkout Gateway

Public application-facing checkout entry point.
The legacy CheckoutService is intentionally not exposed here; all checkout
requests must pass through RevalidationCheckoutService so basket version,
allocation TTL, live price, inventory availability, and row-level locking are
validated immediately before order creation.
"""

from scripts.domain_services import RevalidationCheckoutService


class CanonicalCheckoutGateway:
    """Single canonical application-facing checkout entry point."""

    @staticmethod
    def checkout(cur, basket_id: str, plan_id: str, retailer_id: str,
                 idempotency_key: str, address_snapshot: dict,
                 vendor_allocations: list) -> dict:
        return RevalidationCheckoutService.revalidate_and_checkout(
            cur=cur,
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            idempotency_key=idempotency_key,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )
