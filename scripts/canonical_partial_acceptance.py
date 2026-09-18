"""Canonical two-party partial-acceptance order lifecycle."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from uuid import NAMESPACE_URL, uuid4, uuid5


class CanonicalPartialAcceptanceService:
    """Vendor proposal + retailer approval/decline for SUBMITTED orders."""

    @staticmethod
    def _fingerprint(items):
        canonical = json.dumps(
            sorted(
                [
                    {
                        "order_item_id": str(item["order_item_id"]),
                        "accepted_quantity": int(item["accepted_quantity"]),
                        "reason": (item.get("reason") or "").strip(),
                    }
                    for item in items
                ],
                key=lambda item: item["order_item_id"],
            ),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _proposal_payload(cur, proposal_id):
        cur.execute(
            """
            SELECT p.id, p.order_id, p.vendor_id, p.retailer_id,
                   p.status, p.decision_reason, p.decided_at
            FROM order_partial_acceptance_proposals p
            WHERE p.id = %s
            """,
            (proposal_id,),
        )
        row = cur.fetchone()
        if not row:
            raise KeyError(f"Partial acceptance proposal {proposal_id} not found.")

        cur.execute(
            """
            SELECT order_item_id, accepted_quantity, reason
            FROM order_partial_acceptance_proposal_items
            WHERE proposal_id = %s
            ORDER BY order_item_id
            """,
            (proposal_id,),
        )
        items = cur.fetchall()
        return {
            "proposal_id": str(row["id"]),
            "order_id": str(row["order_id"]),
            "vendor_id": str(row["vendor_id"]),
            "retailer_id": str(row["retailer_id"]),
            "status": row["status"],
            "decision_reason": row["decision_reason"],
            "decided_at": row["decided_at"].isoformat() if row["decided_at"] else None,
            "items": [
                {
                    "order_item_id": str(item["order_item_id"]),
                    "accepted_quantity": int(item["accepted_quantity"]),
                    "reason": item["reason"],
                }
                for item in items
            ],
        }

    @classmethod
    def propose(
        cls,
        cur,
        *,
        user_id: str,
        organization_id: str,
        order_id: str,
        idempotency_key: str,
        items: list[dict],
    ):
        if not organization_id:
            raise PermissionError(
                "Partial acceptance proposal requires an active vendor organization."
            )
        if not idempotency_key:
            raise ValueError("Partial acceptance proposal requires an idempotency key.")
        if not items:
            raise ValueError("Partial acceptance proposal requires at least one item.")

        fingerprint = cls._fingerprint(items)

        cur.execute(
            """
            SELECT id, request_fingerprint
            FROM order_partial_acceptance_proposals
            WHERE order_id = %s
              AND idempotency_key = %s
            """,
            (order_id, idempotency_key),
        )
        replay = cur.fetchone()
        if replay:
            if replay["request_fingerprint"] != fingerprint:
                raise ValueError(
                    "Idempotency key was already used with a different partial-acceptance payload."
                )
            return cls._proposal_payload(cur, replay["id"]) | {"idempotent_replay": True}

        cur.execute(
            """
            SELECT o.id, o.order_number, o.order_group_id, o.order_status,
                   o.retailer_id, o.vendor_id,
                   v.organization_id AS vendor_organization_id,
                   r.organization_id AS retailer_organization_id
            FROM orders o
            JOIN vendors v ON v.id = o.vendor_id
            JOIN retailers r ON r.id = o.retailer_id
            JOIN organizations vo ON vo.id = v.organization_id
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
        if order["order_status"] != "SUBMITTED":
            raise ValueError(
                f"Partial acceptance proposal requires SUBMITTED order; got {order['order_status']}."
            )

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
                "A pending partial acceptance proposal already exists for this order."
            )

        cur.execute(
            """
            SELECT id, ordered_quantity
            FROM order_items
            WHERE order_id = %s
            FOR UPDATE
            """,
            (order_id,),
        )
        order_items = cur.fetchall()
        item_map = {str(row["id"]): row for row in order_items}
        if not item_map:
            raise ValueError("Order has no order items.")

        seen = set()
        normalized = []
        has_shortage = False
        for item in items:
            item_id = str(item["order_item_id"])
            if item_id in seen:
                raise ValueError(
                    f"Duplicate order item {item_id} in partial acceptance proposal."
                )
            seen.add(item_id)
            row = item_map.get(item_id)
            if not row:
                raise ValueError(f"Order item {item_id} does not belong to this order.")

            accepted_quantity = int(item["accepted_quantity"])
            ordered_quantity = int(row["ordered_quantity"])
            if accepted_quantity <= 0 or accepted_quantity > ordered_quantity:
                raise ValueError(
                    f"Accepted quantity for item {item_id} must be between 1 and {ordered_quantity}."
                )

            reason = (item.get("reason") or "").strip()
            if accepted_quantity < ordered_quantity:
                has_shortage = True
                if not reason:
                    raise ValueError(
                        f"Reason is required for reduced accepted quantity on item {item_id}."
                    )

            normalized.append(
                {
                    "order_item_id": item_id,
                    "accepted_quantity": accepted_quantity,
                    "reason": reason or None,
                }
            )

        if not has_shortage:
            raise ValueError(
                "Partial acceptance proposal must reduce at least one requested quantity."
            )

        proposal_id = str(uuid4())
        cur.execute(
            """
            INSERT INTO order_partial_acceptance_proposals (
                id, order_id, vendor_id, retailer_id,
                proposed_by_user_id, status,
                idempotency_key, request_fingerprint
            )
            VALUES (%s, %s, %s, %s, %s, 'PENDING', %s, %s)
            """,
            (
                proposal_id,
                order_id,
                order["vendor_id"],
                order["retailer_id"],
                user_id,
                idempotency_key,
                fingerprint,
            ),
        )

        for item in normalized:
            cur.execute(
                """
                INSERT INTO order_partial_acceptance_proposal_items (
                    proposal_id, order_item_id, accepted_quantity, reason
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    proposal_id,
                    item["order_item_id"],
                    item["accepted_quantity"],
                    item["reason"],
                ),
            )

        cur.execute(
            """
            SELECT om.user_id, om.organization_id
            FROM organization_memberships om
            JOIN organizations org ON org.id = om.organization_id
            WHERE om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
              AND org.status = 'ACTIVE'
            ORDER BY om.user_id
            """,
            (order["retailer_organization_id"],),
        )
        recipients = cur.fetchall()
        if not recipients:
            raise ValueError("Order has no active retailer recipient membership.")

        for recipient in recipients:
            dedupe_key = (
                f"ORDER_PARTIAL_ACCEPTANCE_PROPOSED:{order_id}:"
                f"{proposal_id}:{recipient['organization_id']}:{recipient['user_id']}"
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
                    gen_random_uuid(), %s,
                    'ORDER_PARTIAL_ACCEPTANCE_PROPOSED', 'ORDER', %s,
                    jsonb_build_object(
                        'order_id', %s,
                        'order_number', %s,
                        'proposal_id', %s,
                        'items', (
                            SELECT COALESCE(
                                jsonb_agg(
                                    jsonb_build_object(
                                        'order_item_id', order_item_id,
                                        'accepted_quantity', accepted_quantity,
                                        'reason', reason
                                    ) ORDER BY order_item_id
                                ),
                                '[]'::jsonb
                            )
                            FROM order_partial_acceptance_proposal_items
                            WHERE proposal_id = %s
                        )
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
                    order["order_number"],
                    proposal_id,
                    proposal_id,
                    recipient["user_id"],
                    recipient["organization_id"],
                    dedupe_key,
                ),
            )

        return cls._proposal_payload(cur, proposal_id)

    @classmethod
    def approve(
        cls,
        cur,
        *,
        user_id: str,
        organization_id: str,
        order_id: str,
        proposal_id: str,
    ):
        if not organization_id:
            raise PermissionError(
                "Partial acceptance approval requires an active retailer organization."
            )

        cur.execute(
            """
            SELECT p.id AS proposal_id,
                   p.order_id,
                   p.vendor_id,
                   p.retailer_id,
                   p.status AS proposal_status,
                   o.order_number,
                   o.order_group_id,
                   o.order_status,
                   o.total_amount_toman AS old_order_total,
                   v.organization_id AS vendor_organization_id,
                   r.organization_id AS retailer_organization_id
            FROM order_partial_acceptance_proposals p
            JOIN orders o ON o.id = p.order_id
            JOIN vendors v ON v.id = o.vendor_id
            JOIN retailers r ON r.id = o.retailer_id
            JOIN organizations vo ON vo.id = v.organization_id
            JOIN organizations ro ON ro.id = r.organization_id
            JOIN organization_memberships om
              ON om.organization_id = r.organization_id
             AND om.user_id = %s
            WHERE p.id = %s
              AND p.order_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
              AND vo.status = 'ACTIVE'
              AND ro.status = 'ACTIVE'
              AND v.status = 'ACTIVE'
              AND r.status = 'ACTIVE'
            FOR UPDATE OF p, o
            """,
            (user_id, proposal_id, order_id, organization_id),
        )
        proposal = cur.fetchone()
        if not proposal:
            raise PermissionError(
                "Partial acceptance proposal is not accessible from the active retailer organization."
            )
        if proposal["proposal_status"] != "PENDING":
            raise ValueError(
                f"Partial acceptance proposal cannot be approved from status {proposal['proposal_status']}."
            )
        if proposal["order_status"] != "SUBMITTED":
            raise ValueError(
                f"Partial acceptance proposal cannot be approved for order status {proposal['order_status']}."
            )

        cur.execute(
            """
            SELECT id, vendor_product_id, ordered_quantity, unit_price_toman
            FROM order_items
            WHERE order_id = %s
            ORDER BY vendor_product_id, id
            FOR UPDATE
            """,
            (order_id,),
        )
        order_items = cur.fetchall()
        if not order_items:
            raise ValueError("Order has no order items.")

        cur.execute(
            """
            SELECT order_item_id, accepted_quantity, reason
            FROM order_partial_acceptance_proposal_items
            WHERE proposal_id = %s
            ORDER BY order_item_id
            """,
            (proposal_id,),
        )
        proposal_items = {
            str(row["order_item_id"]): row
            for row in cur.fetchall()
        }

        active_by_vendor_product = defaultdict(list)
        cur.execute(
            """
            SELECT id, vendor_product_id, quantity, status
            FROM inventory_reservations
            WHERE order_id = %s
            ORDER BY vendor_product_id, id
            FOR UPDATE
            """,
            (order_id,),
        )
        for reservation in cur.fetchall():
            if reservation["status"] != "ACTIVE":
                raise ValueError(
                    f"Order reservation {reservation['id']} is not ACTIVE."
                )
            active_by_vendor_product[str(reservation["vendor_product_id"])].append(
                reservation
            )

        group_old_total = None
        if proposal["order_group_id"]:
            cur.execute(
                """
                SELECT total_amount_toman
                FROM order_groups
                WHERE id = %s
                FOR UPDATE
                """,
                (proposal["order_group_id"],),
            )
            group = cur.fetchone()
            if not group:
                raise ValueError("Order group for partial acceptance was not found.")
            group_old_total = int(group["total_amount_toman"])

        new_total = 0
        consumed_count = 0
        changed_item_count = 0

        for item in order_items:
            item_id = str(item["id"])
            proposed = proposal_items.get(item_id)
            accepted_quantity = (
                int(proposed["accepted_quantity"])
                if proposed
                else int(item["ordered_quantity"])
            )
            ordered_quantity = int(item["ordered_quantity"])

            if accepted_quantity <= 0 or accepted_quantity > ordered_quantity:
                raise ValueError(
                    f"Accepted quantity for item {item_id} must be between 1 and {ordered_quantity}."
                )
            if accepted_quantity < ordered_quantity:
                changed_item_count += 1
            new_total += accepted_quantity * int(item["unit_price_toman"])

            matching = active_by_vendor_product.get(
                str(item["vendor_product_id"]), []
            )
            if len(matching) != 1:
                raise ValueError(
                    f"Partial acceptance requires exactly one active reservation for order item {item_id}."
                )

            reservation = matching[0]
            if int(reservation["quantity"]) != ordered_quantity:
                raise ValueError(
                    f"Reservation quantity does not match ordered quantity for item {item_id}."
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
            if int(inventory["physical_quantity"]) < accepted_quantity:
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
                    accepted_quantity,
                    reservation["quantity"],
                    reservation["vendor_product_id"],
                ),
            )

            cur.execute(
                """
                UPDATE inventory_reservations
                SET status = 'CONSUMED',
                    consumed_quantity = %s,
                    consumed_at = now(),
                    released_at = CASE
                        WHEN %s < quantity THEN now()
                        ELSE released_at
                    END
                WHERE id = %s
                """,
                (
                    accepted_quantity,
                    accepted_quantity,
                    reservation["id"],
                ),
            )
            consumed_count += 1

            cur.execute(
                """
                UPDATE order_items
                SET accepted_quantity = %s,
                    total_line_amount_toman = %s,
                    fulfillment_status = CASE
                        WHEN %s < ordered_quantity THEN 'SHORTAGE'
                        ELSE 'PENDING'
                    END
                WHERE id = %s
                """,
                (
                    accepted_quantity,
                    accepted_quantity * int(item["unit_price_toman"]),
                    accepted_quantity,
                    item_id,
                ),
            )

        if changed_item_count < 1:
            raise ValueError(
                "Partial acceptance approval must reduce at least one requested quantity."
            )

        cur.execute(
            """
            UPDATE orders
            SET order_status = 'PARTIALLY_ACCEPTED',
                total_amount_toman = %s,
                updated_at = now()
            WHERE id = %s
            RETURNING id, order_number, order_group_id, order_status, total_amount_toman
            """,
            (new_total, order_id),
        )
        accepted = cur.fetchone()

        if group_old_total is not None:
            group_new_total = (
                group_old_total - int(proposal["old_order_total"]) + new_total
            )
            cur.execute(
                """
                UPDATE order_groups
                SET total_amount_toman = %s
                WHERE id = %s
                """,
                (group_new_total, proposal["order_group_id"]),
            )

        cur.execute(
            """
            UPDATE order_partial_acceptance_proposals
            SET status = 'ACCEPTED',
                decision_by_user_id = %s,
                decided_at = now(),
                updated_at = now()
            WHERE id = %s
            """,
            (user_id, proposal_id),
        )

        cur.execute(
            """
            SELECT om.user_id, om.organization_id, 'RETAILER' AS recipient_kind
            FROM organization_memberships om
            JOIN organizations org ON org.id = om.organization_id
            WHERE om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
              AND org.status = 'ACTIVE'
            UNION ALL
            SELECT om.user_id, om.organization_id, 'VENDOR' AS recipient_kind
            FROM organization_memberships om
            JOIN organizations org ON org.id = om.organization_id
            WHERE om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
              AND org.status = 'ACTIVE'
            ORDER BY recipient_kind, organization_id, user_id
            """,
            (
                proposal["retailer_organization_id"],
                proposal["vendor_organization_id"],
            ),
        )
        recipients = cur.fetchall()
        if not recipients:
            raise ValueError(
                "Partial acceptance approval has no active recipient membership."
            )

        for recipient in recipients:
            dedupe_key = (
                f"ORDER_PARTIALLY_ACCEPTED:{order_id}:{proposal_id}:"
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
                    gen_random_uuid(), %s,
                    'ORDER_PARTIALLY_ACCEPTED', 'ORDER', %s,
                    jsonb_build_object(
                        'order_id', %s,
                        'order_number', %s,
                        'proposal_id', %s,
                        'order_status', 'PARTIALLY_ACCEPTED',
                        'total_amount_toman', %s,
                        'consumed_reservation_count', %s
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
                    proposal_id,
                    new_total,
                    consumed_count,
                    recipient["user_id"],
                    recipient["organization_id"],
                    dedupe_key,
                ),
            )

        return {
            "proposal_id": str(proposal_id),
            "order_id": str(accepted["id"]),
            "order_number": accepted["order_number"],
            "order_group_id": str(accepted["order_group_id"]),
            "order_status": accepted["order_status"],
            "total_amount_toman": int(accepted["total_amount_toman"]),
            "consumed_reservation_count": consumed_count,
            "changed_item_count": changed_item_count,
        }

    @classmethod
    def decline(
        cls,
        cur,
        *,
        user_id: str,
        organization_id: str,
        order_id: str,
        proposal_id: str,
        reason: str | None = None,
    ):
        if not organization_id:
            raise PermissionError(
                "Partial acceptance decline requires an active retailer organization."
            )
        decision_reason = (reason or "").strip() or None

        cur.execute(
            """
            SELECT p.id AS proposal_id,
                   p.status AS proposal_status,
                   o.id AS order_id,
                   o.order_number,
                   o.order_status,
                   v.organization_id AS vendor_organization_id,
                   r.organization_id AS retailer_organization_id
            FROM order_partial_acceptance_proposals p
            JOIN orders o ON o.id = p.order_id
            JOIN vendors v ON v.id = o.vendor_id
            JOIN retailers r ON r.id = o.retailer_id
            JOIN organizations vo ON vo.id = v.organization_id
            JOIN organizations ro ON ro.id = r.organization_id
            JOIN organization_memberships om
              ON om.organization_id = r.organization_id
             AND om.user_id = %s
            WHERE p.id = %s
              AND p.order_id = %s
              AND om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF')
              AND vo.status = 'ACTIVE'
              AND ro.status = 'ACTIVE'
              AND v.status = 'ACTIVE'
              AND r.status = 'ACTIVE'
            FOR UPDATE OF p, o
            """,
            (user_id, proposal_id, order_id, organization_id),
        )
        proposal = cur.fetchone()
        if not proposal:
            raise PermissionError(
                "Partial acceptance proposal is not accessible from the active retailer organization."
            )
        if proposal["proposal_status"] != "PENDING":
            raise ValueError(
                f"Partial acceptance proposal cannot be declined from status {proposal['proposal_status']}."
            )
        if proposal["order_status"] != "SUBMITTED":
            raise ValueError(
                f"Partial acceptance proposal cannot be declined for order status {proposal['order_status']}."
            )

        cur.execute(
            """
            UPDATE order_partial_acceptance_proposals
            SET status = 'DECLINED',
                decision_by_user_id = %s,
                decision_reason = %s,
                decided_at = now(),
                updated_at = now()
            WHERE id = %s
            """,
            (user_id, decision_reason, proposal_id),
        )

        cur.execute(
            """
            SELECT om.user_id, om.organization_id
            FROM organization_memberships om
            JOIN organizations org ON org.id = om.organization_id
            WHERE om.organization_id = %s
              AND om.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER', 'VENDOR_STAFF')
              AND org.status = 'ACTIVE'
            ORDER BY om.user_id
            """,
            (proposal["vendor_organization_id"],),
        )
        recipients = cur.fetchall()
        if not recipients:
            raise ValueError(
                "Partial acceptance decline has no active vendor recipient membership."
            )

        for recipient in recipients:
            dedupe_key = (
                f"ORDER_PARTIAL_ACCEPTANCE_DECLINED:{order_id}:{proposal_id}:"
                f"{recipient['organization_id']}:{recipient['user_id']}"
            )
            event_id = str(uuid5(NAMESPACE_URL, dedupe_key))
            cur.execute(
                """
                INSERT INTO outbox_events (
                    id, event_id, event_name, aggregate_type, aggregate_id, payload,
                    status, target_user_id, target_organization_id, dedupe_key, channel_hint
                )
                VALUES (
                    gen_random_uuid(), %s,
                    'ORDER_PARTIAL_ACCEPTANCE_DECLINED', 'ORDER', %s,
                    jsonb_build_object(
                        'order_id', %s,
                        'order_number', %s,
                        'proposal_id', %s,
                        'order_status', 'SUBMITTED',
                        'decision_reason', %s
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
                    proposal["order_number"],
                    proposal_id,
                    decision_reason,
                    recipient["user_id"],
                    recipient["organization_id"],
                    dedupe_key,
                ),
            )

        return cls._proposal_payload(cur, proposal_id) | {
            "order_status": "SUBMITTED",
            "decision_reason": decision_reason,
        }
