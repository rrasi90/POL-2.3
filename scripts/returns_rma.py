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

    OPS_ROLES = {"ADMIN_SUPER", "OPS_AGENT", "SUPER_ADMIN", "OPS_ADMIN"}

    @staticmethod
    def _retailer_access(cur, user_id: str, retailer_id: str, organization_id: str | None = None) -> bool:
        sql = """
            SELECT 1
            FROM retailers r
            JOIN organization_memberships om ON om.organization_id = r.organization_id
            JOIN organizations o ON o.id = r.organization_id
            WHERE r.id = %s
              AND om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
        """
        params = [retailer_id, user_id]
        sql += " AND om.organization_id = %s"
        params.append(organization_id)
        sql += "\n            LIMIT 1"
        cur.execute(sql, params)
        return cur.fetchone() is not None

    @staticmethod
    def _vendor_access(cur, user_id: str, vendor_id: str, organization_id: str | None = None) -> bool:
        sql = """
            SELECT 1
            FROM vendors v
            JOIN organization_memberships om ON om.organization_id = v.organization_id
            JOIN organizations o ON o.id = om.organization_id
            WHERE v.id = %s
              AND om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
        """
        params = [vendor_id, user_id]
        sql += " AND om.organization_id = %s"
        params.append(organization_id)
        sql += "\n            LIMIT 1"
        cur.execute(sql, params)
        return cur.fetchone() is not None

    @classmethod
    def _ops_access(cls, cur, user_id: str, organization_id: str | None = None) -> bool:
        sql = """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id = %s
              AND om.status = 'ACTIVE'
              AND o.status = 'ACTIVE'
              AND o.org_type = 'OPERATOR'
              AND om.role = ANY(%s)
        """
        params = [user_id, sorted(cls.OPS_ROLES)]
        sql += " AND om.organization_id = %s"
        params.append(organization_id)
        sql += "\n            LIMIT 1"
        cur.execute(sql, params)
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
                       reason: str, idempotency_key: str, claimed_refund_amount_toman: int,
                       organization_id: str | None = None):
        if not organization_id:
            raise ReturnAccessError("RMA requires an active organization context.")
        if not idempotency_key:
            raise ValueError("Return request requires an idempotency key.")
        if claimed_refund_amount_toman < 0:
            raise ValueError("Claimed refund amount cannot be negative.")
        cur.execute("SELECT * FROM returns WHERE request_idempotency_key = %s", (idempotency_key,))
        existing = cur.fetchone()
        if existing:
            if not cls._retailer_access(cur, actor_user_id, str(existing["retailer_id"]), organization_id):
                raise ReturnAccessError("Only an active retailer member may replay an RMA for the order.")
            if str(existing["order_id"]) != str(order_id):
                raise ReturnStateError("Return idempotency key is bound to another order.")
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
            FOR UPDATE OF o, oi;
            """,
            (order_id,),
        )
        rows = cur.fetchall()
        if not rows:
            raise KeyError("Order not found or not return-eligible")
        retailer_id = str(rows[0]["retailer_id"])
        vendor_id = str(rows[0]["vendor_id"])
        if not cls._retailer_access(cur, actor_user_id, retailer_id, organization_id):
            raise ReturnAccessError("Only an active retailer member may open an RMA for the order.")
        if any(str(r["vendor_id"]) != vendor_id for r in rows):
            raise ValueError("A child order must have one canonical vendor before an MVP RMA is opened.")
        order_item_map = {str(r["order_item_id"]): r for r in rows}
        if not order_items:
            raise ValueError("At least one return item is required.")

        # Aggregate by order item before validating. Duplicate request lines must
        # never bypass the per-item returnable quantity ceiling.
        requested_by_item = {}
        reason_by_item = {}
        unit_refund_by_item = {}
        for item in order_items:
            item_key = str(item["order_item_id"])
            if item_key not in order_item_map:
                raise ValueError("Return item does not belong to the order.")
            quantity = int(item["quantity"])
            reason_code = item.get("reason_code", "OTHER")
            if quantity <= 0:
                raise ValueError("Return quantity must be positive.")
            if reason_code not in {"DAMAGED", "SHORTAGE", "WRONG_ITEM", "QUALITY", "DELIVERY_ERROR", "OTHER"}:
                raise ValueError("Unsupported RMA reason code.")
            requested_by_item[item_key] = requested_by_item.get(item_key, 0) + quantity
            reason_by_item.setdefault(item_key, reason_code)
            if item.get("unit_refund_amount_toman") is not None:
                unit_refund_by_item[item_key] = int(item["unit_refund_amount_toman"])

        claim_ceiling = 0
        for item_key, quantity in requested_by_item.items():
            source = order_item_map[item_key]
            delivered = int(source["delivered_quantity"] or 0)
            cur.execute(
                """
                SELECT COALESCE(SUM(
                    CASE
                      WHEN r.status IN (
                        'RETURN_REQUESTED','APPROVED','PICKUP_REQUIRED',
                        'RETURN_IN_TRANSIT','RECEIVED','VENDOR_INSPECTION','REFUND_PENDING'
                      ) THEN ri.requested_quantity
                      WHEN r.status IN ('ACCEPTED','REFUNDED','CLOSED') THEN ri.accepted_quantity
                      ELSE 0
                    END
                ),0) AS consumed_quantity
                FROM return_items ri
                JOIN returns r ON r.id = ri.return_id
                WHERE ri.order_item_id = %s
                  AND r.order_id = %s
                """,
                (item_key, order_id),
            )
            consumed = int(cur.fetchone()["consumed_quantity"])
            max_returnable = max(0, delivered - consumed)
            if quantity > max_returnable:
                raise ValueError(
                    f"Aggregated return quantity exceeds delivered/ordered quantity. Return quantity exceeds remaining returnable quantity: requested={quantity}, remaining={max_returnable}."
                )
            unit_refund = unit_refund_by_item.get(item_key, int(source["unit_price_toman"]))
            claim_ceiling += quantity * unit_refund

        if claimed_refund_amount_toman > claim_ceiling:
            raise ValueError(
                f"Claimed refund amount exceeds line-item ceiling: claimed={claimed_refund_amount_toman}, ceiling={claim_ceiling}."
            )

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
        for item_key, quantity in requested_by_item.items():
            source = order_item_map[item_key]
            # A duplicate line is collapsed into one canonical return_items row.
            source_item = next(i for i in order_items if str(i["order_item_id"]) == item_key)
            line_unit_refund = unit_refund_by_item.get(
                item_key, int(source_item.get("unit_refund_amount_toman") or source["unit_price_toman"])
            )
            cur.execute(
                """
                INSERT INTO return_items
                    (id, return_id, order_item_id, requested_quantity,
                     unit_refund_amount_toman, reason_code)
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (str(uuid.uuid4()), return_id, item_key, quantity,
                 line_unit_refund,
                 reason_by_item[item_key]),
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
    @classmethod
    def _ensure_refund_pending(cls, cur, ret: dict, actor_user_id: str):
        amount = ret["approved_refund_amount_toman"]
        if amount is None or int(amount) <= 0:
            raise ReturnStateError("A positive approved refund amount is required before REFUND_PENDING.")
        if str(ret.get("initiated_by_user_id")) == str(actor_user_id):
            raise ReturnAccessError("Refund approval must be performed by a different actor than the RMA initiator.")

        # Canonical payment provenance: exactly one successful payment must be
        # attributable to the order, otherwise an explicit payment choice is
        # required before an RMA refund can be approved.
        cur.execute(
            """
            SELECT p.*,
                   p.amount_toman - COALESCE((
                       SELECT SUM(r2.amount_toman)
                       FROM refunds r2
                       WHERE r2.payment_id=p.id
                         AND r2.status IN ('PENDING','APPROVED','COMPLETED')
                   ),0) AS refundable_remaining
            FROM payments p
            WHERE p.order_id=%s
              AND p.retailer_id=%s
              AND p.vendor_id=%s
              AND p.payment_status='SUCCESS'
            ORDER BY p.created_at ASC
            FOR UPDATE
            """,
            (ret["order_id"], ret["retailer_id"], ret["vendor_id"]),
        )
        payments = [dict(x) for x in cur.fetchall()]
        eligible = [x for x in payments if int(x["refundable_remaining"]) >= int(amount)]
        if len(eligible) != 1:
            raise ReturnStateError("RMA refund requires exactly one eligible successful payment.")
        payment = eligible[0]

        cur.execute(
            """
            INSERT INTO refunds
                (id, order_id, payment_id, dispute_id, retailer_id, amount_toman,
                 refund_method, reason, status, approved_by_user_id, approved_at,
                 created_by_user_id, return_id, idempotency_key, source_type)
            VALUES
                (%s,%s,%s,NULL,%s,%s,'BANK_REVERSAL',%s,'APPROVED',%s,now(),%s,%s,%s,'RMA')
            ON CONFLICT (return_id) WHERE return_id IS NOT NULL DO NOTHING
            RETURNING id
            """,
            (
                str(uuid.uuid4()), ret["order_id"], payment["id"], ret["retailer_id"],
                amount, f"RMA refund {ret['return_number']}", actor_user_id,
                ret["initiated_by_user_id"], ret["id"], f"rma:{ret['id']}",
            ),
        )
        refund_row = cur.fetchone()
        if refund_row:
            refund_id = refund_row["id"]
            cur.execute("UPDATE returns SET refund_id=%s WHERE id=%s", (refund_id, ret["id"]))
            cur.execute(
                """
                SELECT id
                FROM settlements
                WHERE order_id=%s AND vendor_id=%s
                ORDER BY created_at DESC
                LIMIT 1
                FOR UPDATE
                """,
                (ret["order_id"], ret["vendor_id"]),
            )
            settlement = cur.fetchone()
            if settlement:
                cur.execute(
                    """
                    INSERT INTO settlement_adjustments
                        (id, settlement_id, dispute_id, refund_id, adjustment_type,
                         amount_toman, reason, applied_by_user_id)
                    VALUES (%s,%s,NULL,%s,'REFUND',%s,%s,%s)
                    ON CONFLICT (refund_id) WHERE refund_id IS NOT NULL DO NOTHING
                    """,
                    (
                        str(uuid.uuid4()), settlement["id"], refund_id, amount,
                        f"RMA refund {ret['return_number']}", actor_user_id,
                    ),
                )
                cur.execute(
                    """
                    SELECT COALESCE(SUM(amount_toman),0) AS total
                    FROM settlement_adjustments WHERE settlement_id=%s
                    """,
                    (settlement["id"],),
                )
                total = int(cur.fetchone()["total"])
                cur.execute(
                    """
                    UPDATE settlements
                    SET adjustment_amount_toman=-%s,
                        net_vendor_amount_toman=gross_amount_toman-commission_amount_toman-%s,
                        status='RECONCILED'
                    WHERE id=%s
                    """,
                    (total, total, settlement["id"]),
                )

            cur.execute(
                """
                INSERT INTO outbox_events
                    (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                     target_organization_id,target_user_id,dedupe_key,channel_hint)
                SELECT gen_random_uuid(),%s,'REFUND_CREATED','REFUND',%s,
                       %s::jsonb,'PENDING',om.organization_id,om.user_id,%s,'INBOX'
                FROM organization_memberships om
                WHERE om.organization_id=(SELECT organization_id FROM retailers WHERE id=%s)
                  AND om.status='ACTIVE'
                  AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
                ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                """,
                (
                    f"REFUND_CREATED:{refund_id}", str(refund_id),
                    json.dumps({"refund_id":str(refund_id),"order_id":str(ret["order_id"]),
                                "amount_toman":int(amount),"status":"APPROVED"}),
                    f"REFUND_CREATED:{refund_id}", ret["retailer_id"],
                ),
            )
    @staticmethod
    def _complete_refund(cur, ret: dict, actor_user_id: str):
        if not ret["refund_id"]:
            raise ReturnStateError("Cannot mark RMA REFUNDED without a linked refund.")
        cur.execute(
            "SELECT * FROM refunds WHERE id=%s FOR UPDATE",
            (ret["refund_id"],),
        )
        refund = cur.fetchone()
        if not refund:
            raise ReturnStateError("Linked refund does not exist.")
        if str(refund["approved_by_user_id"]) == str(actor_user_id):
            raise ReturnAccessError("Refund completion must be performed by a different actor than the approver.")
        if refund["status"] != "APPROVED":
            raise ReturnStateError("Linked refund is missing or is not in APPROVED state.")

        cur.execute("SELECT * FROM payments WHERE id=%s FOR UPDATE", (refund["payment_id"],))
        payment = cur.fetchone()
        if not payment or payment["payment_status"] != "SUCCESS":
            raise ReturnStateError("Linked refund payment is missing or not refundable.")

        cur.execute(
            """
            UPDATE payments
            SET payment_status='REFUNDED'
            WHERE id=%s AND payment_status='SUCCESS'
            """,
            (refund["payment_id"],),
        )
        if cur.rowcount != 1:
            raise ReturnStateError("Linked payment is no longer refundable.")

        cur.execute(
            """
            UPDATE refunds
            SET status='COMPLETED', completed_at=now(), completed_by_user_id=%s
            WHERE id=%s AND status='APPROVED'
            RETURNING *
            """,
            (actor_user_id, ret["refund_id"]),
        )
        completed = cur.fetchone()
        if not completed:
            raise ReturnStateError("Refund completion raced with another completion request.")

        for event_name in ("REFUND_COMPLETED", "PAYMENT_REFUNDED"):
            cur.execute(
                """
                INSERT INTO outbox_events
                    (id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                     target_organization_id,target_user_id,dedupe_key,channel_hint)
                SELECT gen_random_uuid(),%s,%s,'REFUND',%s,%s::jsonb,'PENDING',
                       om.organization_id,om.user_id,%s,'INBOX'
                FROM organization_memberships om
                JOIN retailers r ON r.organization_id=om.organization_id
                WHERE r.id=%s AND om.status='ACTIVE'
                  AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
                ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                """,
                (
                    f"{event_name}:{ret['refund_id']}", event_name, str(ret["refund_id"]),
                    json.dumps({"refund_id":str(ret["refund_id"]),"order_id":str(ret["order_id"]),
                                "amount_toman":int(refund["amount_toman"]),"status":"COMPLETED"}),
                    f"{event_name}:{ret['refund_id']}", ret["retailer_id"],
                ),
            )

        cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_before, state_after, reason)
            VALUES (%s,'RMA_REFUND_COMPLETED','REFUND',%s,%s,%s,%s)
            """,
            (
                actor_user_id, ret["refund_id"],
                Json({"status":"APPROVED","payment_status":"SUCCESS"}),
                Json({"status":"COMPLETED","payment_status":"REFUNDED"}),
                f"RMA {ret['return_number']} refund completed",
            ),
        )

    @classmethod
    def transition(cls, cur, actor_user_id: str, return_id: str, target_status: str,
                   reason: str | None = None, approved_refund_amount_toman: int | None = None,
                   organization_id: str | None = None):
        if not organization_id:
            raise ReturnAccessError("RMA transition requires an active organization context.")
        if approved_refund_amount_toman is not None and approved_refund_amount_toman < 0:
            raise ValueError("Approved refund amount cannot be negative.")
        cur.execute("SELECT * FROM returns WHERE id = %s FOR UPDATE", (return_id,))
        ret = cur.fetchone()
        if not ret:
            raise KeyError("Return not found")
        current = ret["status"]
        if target_status not in cls.TRANSITIONS.get(current, set()):
            raise ReturnStateError(f"Invalid RMA transition: {current} -> {target_status}")

        retailer_ok = cls._retailer_access(cur, actor_user_id, str(ret["retailer_id"]), organization_id)
        vendor_ok = cls._vendor_access(cur, actor_user_id, str(ret["vendor_id"]), organization_id)
        ops_ok = cls._ops_access(cur, actor_user_id, organization_id)
        if target_status == "CANCELLED":
            allowed = retailer_ok and current in {"RETURN_REQUESTED", "APPROVED", "PICKUP_REQUIRED"}
        elif target_status in {"APPROVED", "PICKUP_REQUIRED", "RETURN_IN_TRANSIT", "RECEIVED", "VENDOR_INSPECTION", "ACCEPTED", "REJECTED"}:
            allowed = vendor_ok
        elif target_status in {"REFUND_PENDING", "REFUNDED", "CLOSED"}:
            # Financially meaningful states belong to POL operations, not either
            # commercial party. REFUNDED additionally enforces two-person control.
            allowed = ops_ok
        else:
            allowed = False
        if not allowed:
            raise ReturnAccessError("Actor is not authorized for this RMA transition.")

        # Materialize item-level receipt/inspection state at the lifecycle boundary.
        cur.execute(
            """
            SELECT id, requested_quantity, received_quantity, accepted_quantity, unit_refund_amount_toman
            FROM return_items
            WHERE return_id=%s
            ORDER BY id
            FOR UPDATE
            """,
            (return_id,),
        )
        return_lines = cur.fetchall()
        if not return_lines:
            raise ReturnStateError("Return has no return items.")

        calculated_refund = 0
        if target_status == "RECEIVED":
            for line in return_lines:
                cur.execute(
                    """
                    UPDATE return_items
                    SET received_quantity = requested_quantity
                    WHERE id=%s
                    """,
                    (line["id"],),
                )
        elif target_status == "ACCEPTED":
            for line in return_lines:
                cur.execute(
                    """
                    UPDATE return_items
                    SET accepted_quantity = received_quantity
                    WHERE id=%s
                    """,
                    (line["id"],),
                )
            calculated_refund = sum(
                int(line["received_quantity"]) * int(line["unit_refund_amount_toman"])
                for line in return_lines
            )

        next_refund_amount = approved_refund_amount_toman
        if target_status == "ACCEPTED":
            if approved_refund_amount_toman is not None and int(approved_refund_amount_toman) != calculated_refund:
                raise ValueError(
                    f"Approved refund amount must equal accepted return lines: "
                    f"approved={approved_refund_amount_toman}, calculated={calculated_refund}."
                )
            next_refund_amount = calculated_refund
        if target_status == "REFUND_PENDING" and next_refund_amount is None:
            next_refund_amount = ret["approved_refund_amount_toman"]
        if target_status == "REFUND_PENDING" and (next_refund_amount is None or int(next_refund_amount) <= 0):
            raise ReturnStateError("A positive approved refund amount is required before REFUND_PENDING.")

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
            cls._complete_refund(cur, updated, actor_user_id)

        cls._write_event(cur, return_id, current, target_status, actor_user_id, reason)
        return updated
