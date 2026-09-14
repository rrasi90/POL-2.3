"""Canonical Return / RMA application boundary for the asset-light MVP."""

from __future__ import annotations

import uuid


class ReturnAccessError(PermissionError):
    pass


class ReturnStateError(ValueError):
    pass


class CanonicalReturnService:
    TRANSITIONS = {
        "RETURN_REQUESTED": {"APPROVED", "REJECTED", "CANCELLED"},
        "APPROVED": {"PICKUP_REQUIRED", "CANCELLED"},
        "PICKUP_REQUIRED": {"RETURN_IN_TRANSIT", "CANCELLED"},
        "RETURN_IN_TRANSIT": {"RECEIVED", "CANCELLED"},
        "RECEIVED": {"VENDOR_INSPECTION"},
        "VENDOR_INSPECTION": {"ACCEPTED", "REJECTED"},
        "ACCEPTED": {"REFUND_PENDING", "CLOSED"},
        "REFUND_PENDING": {"REFUNDED", "CLOSED"},
        "REFUNDED": {"CLOSED"},
        "REJECTED": {"CLOSED"},
        "CANCELLED": set(),
        "CLOSED": set(),
    }

    @staticmethod
    def _retailer_access(cur, user_id: str, retailer_id: str) -> bool:
        cur.execute(
            """
            SELECT 1
            FROM retailers r
            JOIN organization_memberships om ON om.organization_id = r.organization_id
            JOIN organizations o ON o.id = r.organization_id
            WHERE r.id = %s
              AND om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
            LIMIT 1
            """,
            (retailer_id, user_id),
        )
        return cur.fetchone() is not None

    @staticmethod
    def _vendor_access(cur, user_id: str, vendor_id: str) -> bool:
        cur.execute(
            """
            SELECT 1
            FROM vendors v
            JOIN organization_memberships om ON om.organization_id = v.organization_id
            JOIN organizations o ON o.id = om.organization_id
            WHERE v.id = %s
              AND om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
            LIMIT 1
            """,
            (vendor_id, user_id),
        )
        return cur.fetchone() is not None

    @staticmethod
    def _write_event(cur, return_id: str, from_status: str | None, to_status: str,
                     actor_user_id: str | None, reason: str | None = None):
        cur.execute(
            """
            INSERT INTO return_events
                (id, return_id, from_status, to_status, actor_user_id, reason)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (str(uuid.uuid4()), return_id, from_status, to_status, actor_user_id, reason),
        )

    @classmethod
    def request_return(cls, cur, actor_user_id: str, order_id: str, order_items: list[dict],
                       reason: str, idempotency_key: str, claimed_refund_amount_toman: int):
        if not idempotency_key:
            raise ValueError("Return request requires an idempotency key.")
        if claimed_refund_amount_toman < 0:
            raise ValueError("Claimed refund amount cannot be negative.")
        cur.execute("SELECT * FROM returns WHERE request_idempotency_key = %s", (idempotency_key,))
        existing = cur.fetchone()
        if existing:
            return existing

        cur.execute(
            """
            SELECT o.id, o.retailer_id, o.vendor_id, o.order_status,
                   oi.id AS order_item_id, oi.vendor_product_id, oi.ordered_quantity,
                   oi.delivered_quantity, oi.unit_price_toman
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.id = %s
              AND o.retailer_id IS NOT NULL
              AND o.order_status NOT IN ('CANCELLED','CREATED','SUBMITTED')
            FOR SHARE;
            """,
            (order_id,),
        )
        rows = cur.fetchall()
        if not rows:
            raise KeyError("Order not found or not return-eligible")
        retailer_id = str(rows[0]["retailer_id"])
        vendor_id = str(rows[0]["vendor_id"])
        if not cls._retailer_access(cur, actor_user_id, retailer_id):
            raise ReturnAccessError("Only an active retailer member may open an RMA for the order.")
        if any(str(r["vendor_id"]) != vendor_id for r in rows):
            raise ValueError("A child order must have one canonical vendor before an MVP RMA is opened.")
        order_item_map = {str(r["order_item_id"]): r for r in rows}
        if not order_items:
            raise ValueError("At least one return item is required.")
        for item in order_items:
            item_key = str(item["order_item_id"])
            if item_key not in order_item_map:
                raise ValueError("Return item does not belong to the order.")
            quantity = int(item["quantity"])
            max_returnable = int(order_item_map[item_key]["delivered_quantity"] or order_item_map[item_key]["ordered_quantity"])
            if quantity <= 0 or quantity > max_returnable:
                raise ValueError("Return quantity exceeds delivered/ordered quantity.")
            reason_code = item.get("reason_code", "OTHER")
            if reason_code not in {"DAMAGED", "SHORTAGE", "WRONG_ITEM", "QUALITY", "DELIVERY_ERROR", "OTHER"}:
                raise ValueError("Unsupported RMA reason code.")

        return_id = str(uuid.uuid4())
        return_number = "RMA-" + return_id.replace("-", "")[:12].upper()
        cur.execute(
            """
            INSERT INTO returns
                (id, return_number, order_id, retailer_id, vendor_id, status,
                 reason, claimed_refund_amount_toman, request_idempotency_key,
                 initiated_by_user_id)
            VALUES (%s,%s,%s,%s,%s,'RETURN_REQUESTED',%s,%s,%s,%s)
            RETURNING *;
            """,
            (return_id, return_number, order_id, retailer_id, vendor_id, reason,
             claimed_refund_amount_toman, idempotency_key, actor_user_id),
        )
        ret = cur.fetchone()
        for item in order_items:
            source = order_item_map[str(item["order_item_id"])]
            cur.execute(
                """
                INSERT INTO return_items
                    (id, return_id, order_item_id, requested_quantity,
                     unit_refund_amount_toman, reason_code)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (str(uuid.uuid4()), return_id, item["order_item_id"], int(item["quantity"]),
                 int(item.get("unit_refund_amount_toman") or source["unit_price_toman"]),
                 item.get("reason_code", "OTHER")),
            )
        cls._write_event(cur, return_id, None, "RETURN_REQUESTED", actor_user_id, reason)
        cur.execute(
            """
            INSERT INTO outbox_events
                (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                 target_user_id,target_organization_id,dedupe_key)
            SELECT gen_random_uuid(), %s, 'RETURN_REQUESTED', 'RETURN', %s,
                   jsonb_build_object('return_id', %s, 'order_id', %s), 'PENDING',
                   r.user_id, r.organization_id, %s
            FROM retailers r
            WHERE r.id = %s
            ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING;
            """,
            ("return_requested:" + return_id, return_id, return_id, order_id,
             "return_requested:" + return_id, retailer_id),
        )
        return ret

    @classmethod
    def _ensure_refund_pending(cls, cur, ret: dict, actor_user_id: str):
        amount = ret["approved_refund_amount_toman"]
        if amount is None or int(amount) <= 0:
            raise ReturnStateError("A positive approved refund amount is required before REFUND_PENDING.")
        cur.execute(
            """
            INSERT INTO refunds
                (id, order_id, payment_id, dispute_id, retailer_id, amount_toman,
                 refund_method, reason, status, approved_by_user_id, return_id)
            VALUES
                (%s,%s,NULL,NULL,%s,%s,'VENDOR_CASH_DIRECT',%s,'APPROVED',%s,%s)
            ON CONFLICT (return_id) WHERE return_id IS NOT NULL DO NOTHING
            RETURNING id;
            """,
            (str(uuid.uuid4()), ret["order_id"], ret["retailer_id"], amount,
             f"RMA refund {ret['return_number']}", actor_user_id, ret["id"]),
        )
        refund_row = cur.fetchone()
        if refund_row:
            cur.execute(
                "UPDATE returns SET refund_id=%s WHERE id=%s",
                (refund_row["id"], ret["id"]),
            )

    @staticmethod
    def _complete_refund(cur, ret: dict):
        if not ret["refund_id"]:
            raise ReturnStateError("Cannot mark RMA REFUNDED without a linked refund.")
        cur.execute(
            """
            UPDATE refunds
            SET status='COMPLETED', completed_at=now()
            WHERE id=%s AND status='APPROVED'
            RETURNING id;
            """,
            (ret["refund_id"],),
        )
        if not cur.fetchone():
            raise ReturnStateError("Linked refund is missing or is not in APPROVED state.")

    @classmethod
    def transition(cls, cur, actor_user_id: str, return_id: str, target_status: str,
                   reason: str | None = None, approved_refund_amount_toman: int | None = None):
        if approved_refund_amount_toman is not None and approved_refund_amount_toman < 0:
            raise ValueError("Approved refund amount cannot be negative.")
        cur.execute("SELECT * FROM returns WHERE id = %s FOR UPDATE", (return_id,))
        ret = cur.fetchone()
        if not ret:
            raise KeyError("Return not found")
        current = ret["status"]
        if target_status not in cls.TRANSITIONS.get(current, set()):
            raise ReturnStateError(f"Invalid RMA transition: {current} -> {target_status}")

        retailer_ok = cls._retailer_access(cur, actor_user_id, str(ret["retailer_id"]))
        vendor_ok = cls._vendor_access(cur, actor_user_id, str(ret["vendor_id"]))
        if target_status == "CANCELLED":
            allowed = retailer_ok and current in {"RETURN_REQUESTED", "APPROVED", "PICKUP_REQUIRED"}
        elif target_status in {"APPROVED", "PICKUP_REQUIRED", "RETURN_IN_TRANSIT", "RECEIVED", "VENDOR_INSPECTION", "ACCEPTED", "REJECTED"}:
            allowed = vendor_ok
        elif target_status in {"REFUND_PENDING", "REFUNDED", "CLOSED"}:
            allowed = retailer_ok or vendor_ok
        else:
            allowed = False
        if not allowed:
            raise ReturnAccessError("Actor is not authorized for this RMA transition.")

        next_refund_amount = approved_refund_amount_toman
        if target_status == "REFUND_PENDING" and next_refund_amount is None:
            next_refund_amount = ret["approved_refund_amount_toman"]

        cur.execute(
            """
            UPDATE returns
            SET status = %s,
                approved_refund_amount_toman = COALESCE(%s, approved_refund_amount_toman),
                approved_at = CASE WHEN %s = 'APPROVED' THEN now() ELSE approved_at END,
                received_at = CASE WHEN %s = 'RECEIVED' THEN now() ELSE received_at END,
                inspected_at = CASE WHEN %s IN ('ACCEPTED','REJECTED') THEN now() ELSE inspected_at END,
                resolved_at = CASE WHEN %s IN ('REFUNDED','REJECTED','CANCELLED','CLOSED') THEN COALESCE(resolved_at, now()) ELSE resolved_at END,
                resolution_reason = COALESCE(%s, resolution_reason)
            WHERE id = %s
            RETURNING *;
            """,
            (target_status, next_refund_amount, target_status, target_status,
             target_status, target_status, reason, return_id),
        )
        updated = cur.fetchone()

        if target_status == "REFUND_PENDING":
            cls._ensure_refund_pending(cur, updated, actor_user_id)
            cur.execute("SELECT * FROM returns WHERE id=%s FOR UPDATE", (return_id,))
            updated = cur.fetchone()
        elif target_status == "REFUNDED":
            cls._complete_refund(cur, updated)

        cls._write_event(cur, return_id, current, target_status, actor_user_id, reason)
        return updated
