"""Canonical retailer-side order cancellation and reservation release."""

from __future__ import annotations

from uuid import NAMESPACE_URL, uuid5


class CanonicalRetailerOrderService:
    @classmethod
    def cancel_order(cls, cur, *, user_id: str, organization_id: str, order_id: str, reason: str = "RETAILER_CANCELLED") -> dict:
        if not organization_id:
            raise PermissionError("Retailer cancellation requires an active organization context.")

        normalized_reason = (reason or "RETAILER_CANCELLED").strip()[:64]
        cur.execute(
            """
            SELECT o.id, o.order_number, o.order_group_id, o.order_status, o.retailer_id,
                   o.vendor_id, v.organization_id AS vendor_organization_id,
                   r.organization_id AS retailer_organization_id
            FROM orders o
            JOIN retailers r ON r.id=o.retailer_id
            JOIN vendors v ON v.id=o.vendor_id
            JOIN organization_memberships om
              ON om.organization_id=r.organization_id AND om.user_id=%s
            JOIN organizations ro ON ro.id=r.organization_id
            WHERE o.id=%s
              AND r.organization_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
              AND ro.status='ACTIVE'
            FOR UPDATE OF o
            """,
            (user_id, order_id, organization_id, organization_id),
        )
        order = cur.fetchone()
        if not order:
            raise PermissionError("Order is not accessible from the active retailer organization.")

        if order["order_status"] == "CANCELLED":
            return {
                "order_id": str(order["id"]),
                "order_number": order["order_number"],
                "order_group_id": str(order["order_group_id"]),
                "order_status": "CANCELLED",
                "idempotent_replay": True,
            }

        if order["order_status"] != "SUBMITTED":
            raise ValueError(
                f"Retailer cancellation is only allowed before vendor acceptance; current status is {order['order_status']}."
            )

        cur.execute(
            """
            SELECT id, vendor_product_id, quantity, status
            FROM inventory_reservations
            WHERE order_id=%s
            ORDER BY id
            FOR UPDATE
            """,
            (order_id,),
        )
        reservations = cur.fetchall()
        released_count = 0

        for reservation in reservations:
            if reservation["status"] != "ACTIVE":
                continue
            quantity = int(reservation["quantity"])
            cur.execute(
                """
                SELECT reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id=%s
                FOR UPDATE
                """,
                (reservation["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            if not inventory or int(inventory["reserved_quantity"]) < quantity:
                raise ValueError(
                    f"Reserved inventory is insufficient for cancellation of reservation {reservation['id']}."
                )
            cur.execute(
                """
                UPDATE vendor_inventory
                SET reserved_quantity=reserved_quantity-%s,
                    updated_at=now()
                WHERE vendor_product_id=%s
                """,
                (quantity, reservation["vendor_product_id"]),
            )
            cur.execute(
                """
                UPDATE inventory_reservations
                SET status='RELEASED',
                    consumed_quantity=0,
                    released_at=COALESCE(released_at,now())
                WHERE id=%s AND status='ACTIVE'
                """,
                (reservation["id"],),
            )
            if cur.rowcount == 1:
                released_count += 1

                cur.execute(
                    """
                    INSERT INTO outbox_events (
                        id,event_id,event_name,aggregate_type,aggregate_id,payload,
                        status,target_user_id,target_organization_id,dedupe_key,channel_hint
                    )
                    SELECT gen_random_uuid(),gen_random_uuid(),'INVENTORY_RESERVATION_RELEASED','INVENTORY_RESERVATION',%s,
                        jsonb_build_object(
                            'reservation_id',%s,'order_id',%s,'vendor_product_id',%s,
                            'quantity',%s,'reason','RETAILER_CANCELLED'
                        ),
                        'PENDING',om.user_id,om.organization_id,%s || ':' || om.user_id::text,'INBOX'
                    FROM organization_memberships om
                    WHERE om.organization_id = (SELECT v.organization_id FROM vendors v WHERE v.id = %s)
                      AND om.status='ACTIVE'
                      AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
                    ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                    """,
                    (
                        reservation["id"], reservation["id"], order_id,
                        reservation["vendor_product_id"], reservation["quantity"],
                        f"INVENTORY_RESERVATION_RELEASED:{reservation['id']}",
                        order["vendor_id"],
                        f"reservation-released:{reservation['id']}:RETAILER_CANCELLED"
                    ),
                )

        cur.execute(
            """
            UPDATE orders
            SET order_status='CANCELLED',
                cancellation_reason=%s,
                updated_at=now()
            WHERE id=%s AND order_status='SUBMITTED'
            RETURNING id, order_number, order_group_id, order_status, retailer_id, vendor_id
            """,
            (normalized_reason, order_id),
        )
        cancelled = cur.fetchone()
        if not cancelled:
            raise ValueError("Order cancellation lost its SUBMITTED-state transition.")

        dedupe_key = f"ORDER_CANCELLED:{order_id}:RETAILER"
        cur.execute(
            """
            INSERT INTO outbox_events (
                id,event_id,event_name,aggregate_type,aggregate_id,payload,
                status,target_user_id,target_organization_id,dedupe_key,channel_hint
            )
            SELECT
                gen_random_uuid(),gen_random_uuid(),'ORDER_CANCELLED','ORDER',%s,
                jsonb_build_object(
                    'order_id',%s,
                    'order_number',%s,
                    'order_group_id',%s,
                    'order_status','CANCELLED',
                    'cancellation_reason',%s
                ),
                'PENDING',om.user_id,om.organization_id,%s || ':' || om.user_id::text,'INBOX'
            FROM organization_memberships om
            JOIN organizations org ON org.id=om.organization_id
            WHERE om.organization_id=%s
              AND om.status='ACTIVE'
              AND org.status='ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
            ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
            """,
            (
                order_id, order_id, cancelled["order_number"], str(cancelled["order_group_id"]),
                normalized_reason, dedupe_key, order["vendor_organization_id"],
            ),
        )

        return {
            "order_id": str(cancelled["id"]),
            "order_number": cancelled["order_number"],
            "order_group_id": str(cancelled["order_group_id"]),
            "order_status": cancelled["order_status"],
            "released_reservation_count": released_count,
            "idempotent_replay": False,
        }
