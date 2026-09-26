"""Canonical transactional checkout revalidation service."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone

from psycopg2.extras import Json

from scripts.api.errors import ConflictError

from scripts.sla_calendar import (
    VENDOR_ACCEPTANCE_SLA_HOURS,
    calculate_sla_deadline,
    load_operational_holidays,
)


class RevalidationCheckoutService:
    """Transactional pre-commit checkout verification and reservation."""

    @staticmethod
    def revalidate_and_checkout(
        cur,
        basket_id: str,
        plan_id: str,
        retailer_id: str,
        idempotency_key: str,
        request_fingerprint: str,
        address_snapshot: dict,
        vendor_allocations: list,
    ) -> dict:
        cur.execute(
            """
            SELECT b.id AS basket_id, b.version, b.retailer_id, b.status AS basket_status,
                   p.id AS plan_id, p.basket_id, p.basket_version,
                   p.expires_at, p.status
            FROM baskets b
            JOIN allocation_plans p ON p.id = %s AND p.basket_id = b.id
            WHERE b.id = %s
            FOR UPDATE OF b, p;
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
        if chk["basket_status"] in ("SUBMITTED", "ABANDONED", "EXPIRED"):
            raise ValueError(f"Basket status {chk['basket_status']} cannot accept a new checkout.")
        if chk["version"] != chk["basket_version"]:
            raise ConflictError(f"STALE_BASKET_VERSION: basket v{chk['version']} != plan v{chk['basket_version']}")
        if chk["expires_at"] < datetime.now(timezone.utc):
            raise ValueError("Allocation plan has expired (15-minute TTL exceeded).")
        if not vendor_allocations:
            raise ValueError("Checkout requires at least one allocated basket line.")

        cur.execute(
            """
            SELECT bi.product_id, ai.vendor_id, ai.vendor_product_id,
                   ai.allocated_quantity, ai.unit_price_snapshot_toman, ai.line_total_toman,
                   ai.status
            FROM allocation_items ai
            JOIN basket_items bi ON bi.id = ai.basket_item_id
            WHERE ai.allocation_plan_id = %s AND bi.basket_id = %s
            ORDER BY bi.product_id
            """,
            (plan_id, basket_id),
        )
        persisted = cur.fetchall()
        allocated_statuses = {"ALLOCATED", "PARTIALLY_ALLOCATED"}
        invalid_statuses = {
            row["status"]
            for row in persisted
            if row["status"] not in allocated_statuses and row["status"] != "UNFULFILLED"
        }
        if invalid_statuses:
            raise ValueError(
                f"Checkout cannot consume allocation plan with invalid item statuses: {sorted(invalid_statuses)}"
            )
        # UNFULFILLED lines are a valid allocation-plan outcome. Checkout
        # commits only the vendor-assigned lines; those lines are intentionally
        # excluded from the commercial order payload and total.
        persisted_allocated = [
            row for row in persisted if row["status"] in allocated_statuses
        ]
        expected_allocations = {
            (
                str(row["product_id"]),
                str(row["vendor_id"]),
                str(row["vendor_product_id"]),
                int(row["allocated_quantity"]),
                int(row["unit_price_snapshot_toman"]),
                int(row["line_total_toman"]),
            )
            for row in persisted_allocated
        }
        allocations_by_vendor = defaultdict(list)
        seen_vendor_products = set()
        for alloc in vendor_allocations:
            vp_id = str(alloc["vendor_product_id"])
            if vp_id in seen_vendor_products:
                raise ValueError(f"Duplicate vendor-product allocation in checkout: {vp_id}")
            seen_vendor_products.add(vp_id)
            allocations_by_vendor[str(alloc["vendor_id"])].append(alloc)

            quoted_price = alloc["unit_price_toman"]
            req_qty = alloc["quantity"]
            cur.execute(
                """
                SELECT vp.vendor_id,
                       vp.product_id,
                       vp.vendor_sku,
                       vp.packaging_unit,
                       vp.pack_quantity,
                       vp.is_active,
                       vp.listing_status,
                       v.status AS vendor_status,
                       vi.moq,
                       vp_price.price_toman,
                       p.canonical_name_fa AS product_name_snapshot,
                       b.name_fa AS brand_name_snapshot
                FROM vendor_products vp
                JOIN vendors v ON v.id = vp.vendor_id
                JOIN products p ON p.id = vp.product_id
                JOIN brands b ON b.id = p.brand_id
                LEFT JOIN vendor_inventory vi ON vi.vendor_product_id = vp.id
                LEFT JOIN vendor_prices vp_price ON vp_price.vendor_product_id = vp.id
                 AND vp_price.is_current = TRUE
                WHERE vp.id = %s;
                """,
                (vp_id,),
            )
            offer = cur.fetchone()
            if not offer:
                raise ValueError(f"Vendor product not found: {vp_id}")
            if str(offer["vendor_id"]) != str(alloc["vendor_id"]):
                raise ValueError(f"Vendor allocation mismatch for SKU {vp_id}")
            if offer["vendor_status"] != "ACTIVE" or not offer["is_active"] or offer["listing_status"] != "ACTIVE":
                raise ValueError(f"Vendor product is not currently orderable: {vp_id}")
            if offer["price_toman"] != quoted_price:
                actual = offer["price_toman"] if offer["price_toman"] is not None else "N/A"
                raise ValueError(f"Price freshness failure for SKU {vp_id}: Quoted {quoted_price} vs Live {actual}")
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

            alloc["_product_id"] = str(offer["product_id"])
            alloc["product_id"] = str(offer["product_id"])
            alloc["_product_name_snapshot"] = offer["product_name_snapshot"]
            alloc["_brand_name_snapshot"] = offer["brand_name_snapshot"]
            alloc["_vendor_sku_snapshot"] = offer["vendor_sku"]
            alloc["_packaging_unit_snapshot"] = offer["packaging_unit"]
            alloc["_pack_quantity_snapshot"] = offer["pack_quantity"]

        supplied_allocations = {
            (
                str(a["_product_id"]),
                str(a["vendor_id"]),
                str(a["vendor_product_id"]),
                int(a["quantity"]),
                int(a["unit_price_toman"]),
                int(a["amount_toman"]),
            )
            for a in vendor_allocations
        }
        if len(persisted_allocated) != len(vendor_allocations) or expected_allocations != supplied_allocations:
            raise ValueError("Checkout allocation payload does not exactly match the persisted Allocation Plan.")

        total_toman = sum(v["amount_toman"] for v in vendor_allocations)
        vendor_count = len(allocations_by_vendor)
        og_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO order_groups (
                id, basket_id, allocation_plan_id, retailer_id, checkout_idempotency_key,
                checkout_request_fingerprint, total_amount_toman, order_count, group_status
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE')
            RETURNING id;
            """,
            (og_id, basket_id, plan_id, retailer_id, idempotency_key,
             request_fingerprint, total_toman, vendor_count),
        )

        child_orders = []
        holidays = load_operational_holidays(cur)
        submitted_at = datetime.now(timezone.utc)
        vendor_acceptance_deadline = calculate_sla_deadline(
            submitted_at,
            duration_hours=VENDOR_ACCEPTANCE_SLA_HOURS,
            holidays=holidays,
        )
        for vendor_id, vendor_allocs in allocations_by_vendor.items():
            ord_id = str(uuid.uuid4())
            ord_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            vendor_total = sum(a["amount_toman"] for a in vendor_allocs)
            cur.execute(
                """
                INSERT INTO orders (
                    id, order_group_id, retailer_id, vendor_id, order_number,
                    total_amount_toman, order_status, dispute_status,
                    delivery_address_snapshot, correlation_id,
                    vendor_acceptance_deadline_at
                ) VALUES (%s,%s,%s,%s,%s,%s,'SUBMITTED','NONE',%s,%s,%s)
                RETURNING *;
                """,
                (ord_id, og_id, retailer_id, vendor_id, ord_num, vendor_total,
                 Json(address_snapshot), f"corr-{og_id[:8]}", vendor_acceptance_deadline),
            )
            order_row = cur.fetchone()
            child_orders.append(order_row)

            for alloc in vendor_allocs:
                line_total = int(alloc["quantity"]) * int(alloc["unit_price_toman"])
                cur.execute(
                    """
                    INSERT INTO order_items (
                        id, order_id, product_id, vendor_product_id,
                        product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot,
                        packaging_unit_snapshot, pack_quantity_snapshot,
                        ordered_quantity, accepted_quantity, delivered_quantity,
                        unit_price_toman, total_line_amount_toman, fulfillment_status
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,0,%s,%s,'PENDING')
                    RETURNING *;
                    """,
                    (
                        str(uuid.uuid4()), ord_id, alloc["_product_id"], alloc["vendor_product_id"],
                        alloc["_product_name_snapshot"], alloc["_brand_name_snapshot"],
                        alloc["_vendor_sku_snapshot"], alloc["_packaging_unit_snapshot"],
                        alloc["_pack_quantity_snapshot"], alloc["quantity"],
                        alloc["unit_price_toman"], line_total,
                    ),
                )
                order_item = cur.fetchone()
                order_item_id = str(order_item["id"])

                cur.execute(
                    """
                    INSERT INTO inventory_reservations (
                        id, vendor_product_id, order_id, order_item_id, quantity, status,
                        idempotency_key, expires_at
                    ) VALUES (%s,%s,%s,%s,%s,'ACTIVE',%s,now() + interval '15 minutes');
                    """,
                    (str(uuid.uuid4()), alloc["vendor_product_id"], ord_id, order_item_id,
                     alloc["quantity"], f"res-{idempotency_key}-{alloc['vendor_product_id']}"),
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

        cur.execute(
            """
            UPDATE allocation_plans
            SET status='CONSUMED', consumed_at=now()
            WHERE id=%s AND status='CONFIRMED'
            """,
            (plan_id,),
        )
        if cur.rowcount != 1:
            raise ValueError("Allocation plan could not be consumed exactly once.")

        cur.execute(
            """
            UPDATE baskets
            SET status='SUBMITTED', updated_at=now()
            WHERE id=%s AND status='OPEN'
            """,
            (basket_id,),
        )
        if cur.rowcount != 1:
            raise ValueError("Basket could not be finalized for checkout.")

        RevalidationCheckoutService._enqueue_submission_events(cur, og_id)
        return {"order_group_id": og_id, "order_count": vendor_count, "orders": child_orders}

    @staticmethod
    def _enqueue_submission_events(cur, order_group_id):
        cur.execute(
            """
            SELECT 'ORDER_GROUP_SUBMITTED' AS event_name, 'ORDER_GROUP' AS aggregate_type,
                   og.id AS aggregate_id, om.user_id, om.organization_id,
                   jsonb_build_object('group_id', og.id) AS payload
            FROM order_groups og
            JOIN retailers r ON r.id = og.retailer_id
            JOIN organizations org ON org.id = r.organization_id
            JOIN organization_memberships om ON om.organization_id = org.id
            WHERE og.id = %s AND org.status = 'ACTIVE' AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
            UNION ALL
            SELECT 'ORDER_SUBMITTED', 'ORDER', o.id, om.user_id, om.organization_id,
                   jsonb_build_object('group_id', o.order_group_id,
                                      'order_id', o.id, 'order_number', o.order_number)
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            JOIN organizations org ON org.id = v.organization_id
            JOIN organization_memberships om ON om.organization_id = org.id
            WHERE o.order_group_id = %s AND org.status = 'ACTIVE' AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
            ORDER BY event_name, aggregate_id, organization_id, user_id;
            """,
            (order_group_id, order_group_id),
        )
        for recipient in cur.fetchall():
            dedupe_key = ":".join(str(recipient[key]) for key in (
                "event_name", "aggregate_id", "organization_id", "user_id",
            ))
            event_id = str(uuid.uuid5(uuid.NAMESPACE_URL, dedupe_key))
            cur.execute(
                """
                INSERT INTO outbox_events (
                    id, event_id, event_name, aggregate_type, aggregate_id, payload,
                    status, target_user_id, target_organization_id, dedupe_key, channel_hint
                ) VALUES (%s,%s,%s,%s,%s,%s,'PENDING',%s,%s,%s,'INBOX')
                ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING;
                """,
                (str(uuid.uuid4()), event_id, recipient["event_name"], recipient["aggregate_type"],
                 str(recipient["aggregate_id"]), Json(recipient["payload"]), recipient["user_id"],
                 recipient["organization_id"], dedupe_key),
            )
