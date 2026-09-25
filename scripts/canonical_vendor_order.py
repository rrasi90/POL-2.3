"""Canonical vendor-side order lifecycle services."""

from __future__ import annotations

from uuid import uuid5, NAMESPACE_URL


class CanonicalVendorOrderService:
    """Apply the canonical SUBMITTED -> ACCEPTED transition for one child order."""

    @classmethod
    def accept_order(cls, cur, *, user_id: str, organization_id: str, order_id: str):
        if not organization_id:
            raise PermissionError("Vendor order acceptance requires an active organization context.")

        cur.execute(
            """
            SELECT o.id,
                   o.order_number,
                   o.order_group_id,
                   o.order_status,
                   o.retailer_id,
                   o.vendor_id,
                   o.vendor_acceptance_deadline_at,
                   v.organization_id AS vendor_organization_id,
                   v.status AS vendor_status,
                   ro.id AS retailer_organization_id
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            JOIN organizations vo ON vo.id = v.organization_id
            JOIN retailers r ON r.id = o.retailer_id
            JOIN organizations ro ON ro.id = r.organization_id
            JOIN organization_memberships om
              ON om.organization_id = v.organization_id
             AND om.user_id = %s
            WHERE o.id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
              AND vo.status = 'ACTIVE'
              AND ro.status = 'ACTIVE'
              AND v.status = 'ACTIVE'
            FOR UPDATE OF o
            """,
            (user_id, order_id, organization_id),
        )
        order = cur.fetchone()
        if not order:
            raise PermissionError(
                "Order is not accessible from the active vendor organization."
            )

        if str(order["vendor_organization_id"]) != str(organization_id):
            raise PermissionError(
                "Order vendor does not belong to the active vendor organization."
            )

        if order["order_status"] == "ACCEPTED":
            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM inventory_reservations
                WHERE order_id=%s AND status='CONSUMED'
                """,
                (order_id,),
            )
            consumed_count = int(cur.fetchone()["count"])
            return {
                "order_id": str(order["id"]),
                "order_number": order["order_number"],
                "order_group_id": str(order["order_group_id"]),
                "order_status": "ACCEPTED",
                "total_amount_toman": int(
                    cur.execute(
                        "SELECT total_amount_toman FROM orders WHERE id=%s",
                        (order_id,),
                    ) or 0
                ),
                "accepted_item_count": int(cls._accepted_item_count(cur, order_id)),
                "reservation_count": consumed_count,
                "idempotent_replay": True,
            }

        if order["order_status"] != "SUBMITTED":
            raise ValueError(
                f"Order cannot be accepted from status {order['order_status']}."
            )

        if order["vendor_acceptance_deadline_at"] is not None:
            cur.execute(
                "SELECT now() > %s AS expired",
                (order["vendor_acceptance_deadline_at"],),
            )
            if cur.fetchone()["expired"]:
                raise ValueError("Vendor acceptance deadline has expired.")

        cur.execute(
            """
            SELECT 1
            FROM order_partial_acceptance_proposals
            WHERE order_id = %s
              AND status = 'PENDING'
            LIMIT 1
            """,
            (order_id,),
        )
        if cur.fetchone():
            raise ValueError(
                "Order has a pending partial acceptance proposal awaiting retailer decision."
            )

        cur.execute(
            """
            SELECT ir.id,
                   ir.vendor_product_id,
                   ir.quantity,
                   ir.status
            FROM inventory_reservations ir
            WHERE ir.order_id = %s
            ORDER BY ir.id
            FOR UPDATE
            """,
            (order_id,),
        )
        reservations = cur.fetchall()
        if not reservations:
            raise ValueError("Order has no inventory reservation to consume.")

        for reservation in reservations:
            if reservation["status"] != "ACTIVE":
                raise ValueError(
                    f"Order reservation {reservation['id']} is not ACTIVE."
                )
            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                FOR UPDATE
                """,
                (reservation["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            if not inventory:
                raise ValueError(
                    f"Inventory record not found for SKU {reservation['vendor_product_id']}."
                )
            if int(inventory["reserved_quantity"]) < int(reservation["quantity"]):
                raise ValueError(
                    f"Reserved inventory is insufficient for SKU {reservation['vendor_product_id']}."
                )
            if int(inventory["physical_quantity"]) < int(reservation["quantity"]):
                raise ValueError(
                    f"Physical inventory is insufficient for SKU {reservation['vendor_product_id']}."
                )

            cur.execute(
                """
                UPDATE vendor_inventory
                SET physical_quantity = physical_quantity - %s,
                    reserved_quantity = reserved_quantity - %s,
                    updated_at = now()
                WHERE vendor_product_id = %s
                """,
                (
                    reservation["quantity"],
                    reservation["quantity"],
                    reservation["vendor_product_id"],
                ),
            )
            cur.execute(
                """
                UPDATE inventory_reservations
                SET status = 'CONSUMED',
                    consumed_quantity = quantity,
                    consumed_at = now()
                WHERE id = %s
                """,
                (reservation["id"],),
            )

        cur.execute(
            """
            UPDATE order_items
            SET accepted_quantity = ordered_quantity
            WHERE order_id = %s
            """,
            (order_id,),
        )
        if cur.rowcount < 1:
            raise ValueError("Order has no order items.")

        cur.execute(
            """
            UPDATE orders
            SET order_status = 'ACCEPTED',
                updated_at = now()
            WHERE id = %s
            RETURNING id, order_number, order_group_id, order_status, total_amount_toman
            """,
            (order_id,),
        )
        accepted = cur.fetchone()

        cur.execute(
            """
            INSERT INTO order_timeline_events
                (order_id, event_type, from_status, to_status, actor_user_id, actor_organization_id, event_data)
            VALUES (%s,'ORDER_ACCEPTED','SUBMITTED','ACCEPTED',%s,%s,%s)
            """,
            (
                order_id,
                user_id,
                organization_id,
                '{"source":"vendor_accept"}'::jsonb,
            ),
        )

        cur.execute(
            """
            SELECT om.user_id, om.organization_id
            FROM retailers r
            JOIN organization_memberships om
              ON om.organization_id = r.organization_id
            JOIN organizations ro
              ON ro.id = r.organization_id
            WHERE r.id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
              AND ro.status = 'ACTIVE'
            ORDER BY om.user_id
            """,
            (order["retailer_id"],),
        )
        recipients = cur.fetchall()
        if not recipients:
            raise ValueError("Order has no active retailer recipient membership.")

        for recipient in recipients:
            dedupe_key = (
                f"ORDER_ACCEPTED:{order_id}:"
                f"{recipient['organization_id']}:{recipient['user_id']}"
            )
            event_id = str(uuid5(NAMESPACE_URL, dedupe_key))
            cur.execute(
                """
                INSERT INTO outbox_events (
                    id, event_id, event_name, aggregate_type, aggregate_id,
                    payload, status, target_user_id, target_organization_id,
                    dedupe_key, channel_hint
                )
                VALUES (
                    gen_random_uuid(), %s, 'ORDER_ACCEPTED', 'ORDER', %s,
                    jsonb_build_object(
                        'order_id', %s,
                        'order_number', %s,
                        'order_group_id', %s,
                        'order_status', 'ACCEPTED'
                    ),
                    'PENDING', %s, %s, %s, 'INBOX'
                )
                ON CONFLICT (event_name, dedupe_key)
                WHERE dedupe_key IS NOT NULL
                DO NOTHING
                """,
                (
                    event_id,
                    order_id,
                    order_id,
                    accepted["order_number"],
                    str(accepted["order_group_id"]),
                    recipient["user_id"],
                    recipient["organization_id"],
                    dedupe_key,
                ),
            )

        return {
            "order_id": str(accepted["id"]),
            "order_number": accepted["order_number"],
            "order_group_id": str(accepted["order_group_id"]),
            "order_status": accepted["order_status"],
            "total_amount_toman": int(accepted["total_amount_toman"]),
            "accepted_item_count": int(
                cls._accepted_item_count(cur, order_id)
            ),
            "reservation_count": len(reservations),
        }

    @classmethod
    def reject_order(
        cls,
        cur,
        *,
        user_id: str,
        organization_id: str,
        order_id: str,
        rejection_reason: str,
    ):
        """Apply the canonical SUBMITTED -> REJECTED transition for one child order."""
        if not organization_id:
            raise PermissionError("Vendor order rejection requires an active organization context.")

        reason = (rejection_reason or "").strip()
        cur.execute(
            """
            SELECT o.id,
                   o.order_number,
                   o.order_group_id,
                   o.order_status,
                   o.retailer_id,
                   v.organization_id AS vendor_organization_id
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            JOIN organizations vo ON vo.id = v.organization_id
            JOIN retailers r ON r.id = o.retailer_id
            JOIN organizations ro ON ro.id = r.organization_id
            JOIN organization_memberships om
              ON om.organization_id = v.organization_id
             AND om.user_id = %s
            WHERE o.id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
              AND vo.status = 'ACTIVE'
              AND ro.status = 'ACTIVE'
              AND v.status = 'ACTIVE'
            FOR UPDATE OF o
            """,
            (user_id, order_id, organization_id),
        )
        order = cur.fetchone()
        if not order:
            raise PermissionError(
                "Order is not accessible from the active vendor organization."
            )

        if str(order["vendor_organization_id"]) != str(organization_id):
            raise PermissionError(
                "Order vendor does not belong to the active vendor organization."
            )

        if order["order_status"] == "REJECTED":
            return {
                "order_id": str(order["id"]),
                "order_number": order["order_number"],
                "order_group_id": str(order["order_group_id"]),
                "order_status": "REJECTED",
                "total_amount_toman": int(
                    cur.execute(
                        "SELECT total_amount_toman FROM orders WHERE id=%s",
                        (order_id,),
                    ) or 0
                ),
                "rejection_reason": order.get("rejection_reason"),
                "released_reservation_count": 0,
                "idempotent_replay": True,
            }

        if order["order_status"] != "SUBMITTED":
            raise ValueError(
                f"Order cannot be rejected from status {order['order_status']}."
            )

        if order["vendor_acceptance_deadline_at"] is not None:
            cur.execute(
                "SELECT now() > %s AS expired",
                (order["vendor_acceptance_deadline_at"],),
            )
            if cur.fetchone()["expired"]:
                raise ValueError("Vendor acceptance deadline has expired.")

        cur.execute(
            """
            SELECT 1
            FROM order_partial_acceptance_proposals
            WHERE order_id = %s
              AND status = 'PENDING'
            LIMIT 1
            """,
            (order_id,),
        )
        if cur.fetchone():
            raise ValueError(
                "Order has a pending partial acceptance proposal awaiting retailer decision."
            )

        cur.execute(
            """
            SELECT ir.id,
                   ir.vendor_product_id,
                   ir.quantity,
                   ir.status
            FROM inventory_reservations ir
            WHERE ir.order_id = %s
            ORDER BY ir.id
            FOR UPDATE
            """,
            (order_id,),
        )
        reservations = cur.fetchall()
        if not reservations:
            raise ValueError("Order has no inventory reservation to release.")

        for reservation in reservations:
            if reservation["status"] != "ACTIVE":
                raise ValueError(
                    f"Order reservation {reservation['id']} is not ACTIVE."
                )

            cur.execute(
                """
                SELECT reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                FOR UPDATE
                """,
                (reservation["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            if not inventory:
                raise ValueError(
                    f"Inventory record not found for SKU {reservation['vendor_product_id']}."
                )
            if int(inventory["reserved_quantity"]) < int(reservation["quantity"]):
                raise ValueError(
                    f"Reserved inventory is insufficient for SKU {reservation['vendor_product_id']}."
                )

            cur.execute(
                """
                UPDATE vendor_inventory
                SET reserved_quantity = reserved_quantity - %s,
                    updated_at = now()
                WHERE vendor_product_id = %s
                """,
                (reservation["quantity"], reservation["vendor_product_id"]),
            )
            cur.execute(
                """
                UPDATE inventory_reservations
                SET status = 'RELEASED',
                    consumed_quantity = 0,
                    released_at = now()
                WHERE id = %s
                """,
                (reservation["id"],),
            )

        cur.execute(
            """
            UPDATE orders
            SET order_status = 'REJECTED',
                rejection_reason = %s,
                updated_at = now()
            WHERE id = %s
            RETURNING id, order_number, order_group_id, order_status,
                      total_amount_toman, rejection_reason
            """,
            (reason, order_id),
        )
        rejected = cur.fetchone()

        cur.execute(
            """
            INSERT INTO order_timeline_events
                (order_id, event_type, from_status, to_status, actor_user_id, actor_organization_id, event_data)
            VALUES (%s,'ORDER_REJECTED','SUBMITTED','REJECTED',%s,%s,%s)
            """,
            (
                order_id,
                user_id,
                organization_id,
                '{"source":"vendor_reject"}'::jsonb,
            ),
        )
        cur.execute(
            """
            INSERT INTO vendor_reliability_events
                (vendor_id, event_type, order_id, impact_score, metadata)
            SELECT o.vendor_id, 'ORDER_REJECTED', o.id, 0.00, %s
            FROM orders o
            WHERE o.id = %s
            """,
            ('{"reason":"VENDOR_REJECTED"}'::jsonb, order_id),
        )

        cur.execute(
            """
            SELECT om.user_id, om.organization_id
            FROM retailers r
            JOIN organization_memberships om
              ON om.organization_id = r.organization_id
            JOIN organizations ro
              ON ro.id = r.organization_id
            WHERE r.id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
              AND ro.status = 'ACTIVE'
            ORDER BY om.user_id
            """,
            (order["retailer_id"],),
        )
        recipients = cur.fetchall()
        if not recipients:
            raise ValueError("Order has no active retailer recipient membership.")

        for recipient in recipients:
            dedupe_key = (
                f"ORDER_REJECTED:{order_id}:"
                f"{recipient['organization_id']}:{recipient['user_id']}"
            )
            event_id = str(uuid5(NAMESPACE_URL, dedupe_key))
            cur.execute(
                """
                INSERT INTO outbox_events (
                    id, event_id, event_name, aggregate_type, aggregate_id,
                    payload, status, target_user_id, target_organization_id,
                    dedupe_key, channel_hint
                )
                VALUES (
                    gen_random_uuid(), %s, 'ORDER_REJECTED', 'ORDER', %s,
                    jsonb_build_object(
                        'order_id', %s,
                        'order_number', %s,
                        'order_group_id', %s,
                        'order_status', 'REJECTED',
                        'rejection_reason', %s
                    ),
                    'PENDING', %s, %s, %s, 'INBOX'
                )
                ON CONFLICT (event_name, dedupe_key)
                WHERE dedupe_key IS NOT NULL
                DO NOTHING
                """,
                (
                    event_id,
                    order_id,
                    order_id,
                    rejected["order_number"],
                    str(rejected["order_group_id"]),
                    rejected["rejection_reason"],
                    recipient["user_id"],
                    recipient["organization_id"],
                    dedupe_key,
                ),
            )

        return {
            "order_id": str(rejected["id"]),
            "order_number": rejected["order_number"],
            "order_group_id": str(rejected["order_group_id"]),
            "order_status": rejected["order_status"],
            "total_amount_toman": int(rejected["total_amount_toman"]),
            "rejection_reason": rejected["rejection_reason"],
            "released_reservation_count": len(reservations),
            "idempotent_replay": False,
        }

    @staticmethod
    def _accepted_item_count(cur, order_id: str) -> int:
        cur.execute(
            """
            SELECT COUNT(*) AS count
            FROM order_items
            WHERE order_id = %s
              AND accepted_quantity = ordered_quantity
            """,
            (order_id,),
        )
        return int(cur.fetchone()["count"])
