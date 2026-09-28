"""POL Canonical Checkout Gateway.

The application-facing checkout boundary is responsible for rejecting forged or
stale allocation input and making idempotency deterministic for one request
payload, not merely for one key string.
"""

from __future__ import annotations

import hashlib
import json

from scripts.revalidation_checkout import RevalidationCheckoutService
from scripts.operational_policies import validate_allocation_against_basket


class CanonicalCheckoutGateway:
    """Single canonical application-facing checkout entry point."""

    @staticmethod
    def _fingerprint(*, basket_id, plan_id, retailer_id, address_snapshot, vendor_allocations) -> str:
        payload = {
            "basket_id": str(basket_id),
            "plan_id": str(plan_id),
            "retailer_id": str(retailer_id),
            "address_snapshot": address_snapshot,
            "vendor_allocations": vendor_allocations,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _replay_existing(cur, idempotency_key: str, retailer_id: str, request_fingerprint: str):
        cur.execute(
            """
            SELECT id, retailer_id, total_amount_toman, order_count, group_status,
                   checkout_request_fingerprint
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
        stored_fingerprint = group.get("checkout_request_fingerprint")
        if stored_fingerprint != request_fingerprint:
            raise ValueError("Idempotency key was already used with a different checkout request payload.")
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

        # Serialize the entire checkout transaction for the natural idempotency key.
        # This turns concurrent identical submissions into deterministic replay
        # instead of relying on a uniqueness error from order_groups.
        cur.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0));",
            (str(idempotency_key),),
        )

        request_fingerprint = CanonicalCheckoutGateway._fingerprint(
            basket_id=basket_id,
            plan_id=plan_id,
            retailer_id=retailer_id,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )
        replay = CanonicalCheckoutGateway._replay_existing(
            cur, idempotency_key, retailer_id, request_fingerprint
        )
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
            request_fingerprint=request_fingerprint,
            address_snapshot=address_snapshot,
            vendor_allocations=vendor_allocations,
        )
