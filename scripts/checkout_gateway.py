"""
POL Canonical Checkout Gateway

The application-facing checkout boundary is responsible for:
1. rejecting forged/stale allocation input;
2. making repeated requests with the same idempotency key deterministic; and
3. delegating transactional revalidation to the canonical standalone service.
"""

from scripts.revalidation_checkout import RevalidationCheckoutService
from scripts.operational_policies import validate_allocation_against_basket


class CanonicalCheckoutGateway:
    """Single canonical application-facing checkout entry point."""

    @staticmethod
    def _replay_existing(cur, idempotency_key: str, retailer_id: str):
        cur.execute(
            """
            SELECT id, retailer_id, total_amount_toman, order_count, group_status
            FROM order_groups
            WHERE checkout_idempotency_key = %s;
            """,
            (idempotency_key,),
        )
        group = cur.fetchone()
        if not group:
            return None
        if str(group["retailer_id"]) != str(retailer_id):
            raise ValueError("Idempotency key is already bound to another retailer.")
        cur.execute(
            """
            SELECT * FROM orders
            WHERE order_group_id = %s
            ORDER BY created_at ASC;
            """,
            (group["id"],),
        )
        return {"order_group": group, "orders": cur.fetchall(), "idempotent_replay": True}

    @staticmethod
    def checkout(cur, basket_id: str, plan_id: str, retailer_id: str,
                 idempotency_key: str, address_snapshot: dict,
                 vendor_allocations: list) -> dict:
        if not idempotency_key:
            raise ValueError("Checkout requires a non-empty idempotency key.")

        replay = CanonicalCheckoutGateway._replay_existing(cur, idempotency_key, retailer_id)
        if replay:
            return replay

        validate_allocation_against_basket(
            cur=cur,
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            vendor_allocations=vendor_allocations,
        )

        return RevalidationCheckoutService.revalidate_and_checkout(
            cur=cur,
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            idempotency_key=idempotency_key,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )
