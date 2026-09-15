"""Canonical transactional checkout revalidation service.

This module is intentionally independent from the legacy domain_services module.
The application-facing checkout gateway imports this service directly.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from psycopg2.extras import Json


class RevalidationCheckoutService:
    """Transactional pre-commit checkout verification and reservation."""

    @staticmethod
    def revalidate_and_checkout(
        cur,
        basket_id: str,
        plan_id: str,
        retailer_id: str,
        idempotency_key: str,
        address_snapshot: dict,
        vendor_allocations: list,
    ) -> dict:
        cur.execute(
            """
            SELECT b.version,
                   b.retailer_id,
                   p.basket_id,
                   p.basket_version,
                   p.expires_at,
                   p.status
            FROM baskets b
            JOIN allocation_plans p
              ON p.id = %s
             AND p.basket_id = b.id
            WHERE b.id = %s;
            """,
            (plan_id, basket_id),
        )
        chk = cur.fetchone()
        if not chk:
            raise ValueError("Basket or Allocation Plan not found, or plan does not belong to basket.")
        if str(chk["retailer_id"]) != str(retailer_id):
            raise PermissionError("Checkout retailer does not own the basket.")
        if chk["status"] != "CONFIRMED":
            raise ValueError(f"Allocation plan is not checkout-ready: {chk['status']}")
        if chk["version"] != chk["basket_version"]:
            raise ValueError(
                f"Stale basket checkout: basket v{chk['version']} != plan v{chk['basket_version']}"
            )
        if chk["expires_at"] < datetime.now(timezone.utc):
            raise ValueError("Allocation plan has expired (15-minute TTL exceeded).")

        for alloc in vendor_allocations:
            vp_id = alloc["vendor_product_id"]
            quoted_price = alloc["unit_price_toman"]
            req_qty = alloc["quantity"]

            cur.execute(
                """
                SELECT vp.vendor_id,
                       vp.product_id,
                       vp.pack_quantity,
                       vp.is_active,
                       vp.listing_status,
                       v.status AS vendor_status,
                       vi.moq,
                       vp_price.price_toman
                FROM vendor_products vp
                JOIN vendors v ON v.id = vp.vendor_id
                LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
                LEFT JOIN vendor_prices vp_price
                  ON vp_price.vendor_product_id = vp.id
                 AND vp_price.is_current = TRUE
                WHERE vp.id = %s;
                """,
                (vp_id,),
            )
            offer = cur.fetchone()
            if not offer:
                raise ValueError(f"Vendor product not found: {vp_id}")
            if (
                offer["vendor_status"] != "ACTIVE"
                or not offer["is_active"]
                or offer["listing_status"] != "ACTIVE"
            ):
                raise ValueError(f"Vendor product is not currently orderable: {vp_id}")
            if offer["price_toman"] != quoted_price:
                actual = offer["price_toman"] if offer["price_toman"] is not None else "N/A"
                raise ValueError(
                    f"Price freshness failure for SKU {vp_id}: Quoted {quoted_price} vs Live {actual}"
                )
            if offer["moq"] is not None and req_qty < offer["moq"]:
                raise ValueError(f"MOQ violation for SKU {vp_id}: {req_qty} < {offer['moq']}")

            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                FOR UPDATE;
                """,
                (vp_id,),
            )
            inv_row = cur.fetchone()
            if not inv_row:
                raise ValueError(f"No inventory record found for SKU {vp_id}")
            avail = inv_row["physical_quantity"] - inv_row["reserved_quantity"]
            if avail < req_qty:
                raise ValueError(f"Insufficient stock for SKU {vp_id}: Available {avail} < Requested {req_qty}")

        total_toman = sum(v["amount_toman"] for v in vendor_allocations)
        og_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO order_groups (
                id, basket_id, allocation_plan_id, retailer_id, checkout_idempotency_key,
                total_amount_toman, order_count, group_status
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,'ACTIVE')
            RETURNING id;
            """,
            (og_id, basket_id, plan_id, retailer_id, idempotency_key, total_toman, len(vendor_allocations)),
        )

        child_orders = []
        for alloc in vendor_allocations:
            ord_id = str(uuid.uuid4())
            res_id = str(uuid.uuid4())
            ord_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"

            cur.execute(
                """
                INSERT INTO orders (
                    id, order_group_id, retailer_id, vendor_id, order_number,
                    total_amount_toman, order_status, dispute_status,
                    delivery_address_snapshot, correlation_id
                ) VALUES (%s,%s,%s,%s,%s,%s,'SUBMITTED','NONE',%s,%s)
                RETURNING *;
                """,
                (
                    ord_id,
                    og_id,
                    retailer_id,
                    alloc["vendor_id"],
                    ord_num,
                    alloc["amount_toman"],
                    Json(address_snapshot),
                    f"corr-{og_id[:8]}",
                ),
            )
            child_orders.append(cur.fetchone())

            cur.execute(
                """
                INSERT INTO inventory_reservations (
                    id, vendor_product_id, order_id, quantity, status, idempotency_key, expires_at
                ) VALUES (%s,%s,%s,%s,'ACTIVE',%s,now() + interval '15 minutes');
                """,
                (
                    res_id,
                    alloc["vendor_product_id"],
                    ord_id,
                    alloc["quantity"],
                    f"res-{idempotency_key}-{alloc['vendor_id']}",
                ),
            )

            cur.execute(
                """
                UPDATE vendor_inventory
                SET reserved_quantity = reserved_quantity + %s
                WHERE vendor_product_id = %s
                  AND physical_quantity - reserved_quantity >= %s;
                """,
                (alloc["quantity"], alloc["vendor_product_id"], alloc["quantity"]),
            )
            if cur.rowcount != 1:
                raise ValueError(f"Inventory reservation race detected for SKU {alloc['vendor_product_id']}")

        return {"order_group_id": og_id, "orders": child_orders}
