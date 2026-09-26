"""Canonical finance refund lifecycle for the asset-light non-custodial MVP."""

from __future__ import annotations

from uuid import uuid4
import hashlib

from psycopg2.extras import Json


class RefundService:
    OPS_ROLES = ("OPS_AGENT", "OPS_ADMIN", "ADMIN_SUPER", "SUPER_ADMIN")

    @classmethod
    def _ops_access(cls, cur, user_id: str, organization_id: str) -> bool:
        cur.execute(
            """
            SELECT 1
            FROM organization_memberships om
            JOIN organizations o ON o.id = om.organization_id
            WHERE om.user_id=%s
              AND om.organization_id=%s
              AND om.status='ACTIVE'
              AND o.status='ACTIVE'
              AND o.org_type='OPERATOR'
              AND om.role = ANY(%s)
            LIMIT 1
            """,
            (user_id, organization_id, list(cls.OPS_ROLES)),
        )
        return cur.fetchone() is not None

    @staticmethod
    def _audit(cur, actor_user_id, action, target_id, before, after, reason, correlation_id):
        cur.execute(
            """
            INSERT INTO admin_audit_logs
                (actor_user_id, action, target_entity_type, target_entity_id,
                 state_before, state_after, reason, correlation_id)
            VALUES (%s,%s,'REFUND',%s,%s,%s,%s,%s)
            """,
            (actor_user_id, action, target_id, Json(before), Json(after), reason, correlation_id),
        )

    @staticmethod
    def _event(cur, refund, event_name, actor_user_id, organization_id):
        event_id = f"{event_name}:{refund['id']}"
        dedupe = event_id
        cur.execute(
            """
            SELECT DISTINCT om.user_id, om.organization_id
            FROM organization_memberships om
            JOIN users u ON u.id=om.user_id
            WHERE om.organization_id IN (
                SELECT r.organization_id
                FROM retailers r
                WHERE r.id=%s
                UNION
                SELECT v.organization_id
                FROM orders o
                JOIN vendors v ON v.id=o.vendor_id
                WHERE o.id=%s
            )
              AND om.status='ACTIVE'
              AND u.is_active=TRUE
            ORDER BY om.organization_id, om.user_id
            """,
            (refund["retailer_id"], refund["order_id"]),
        )
        recipients = cur.fetchall()
        for rec in recipients:
            recipient_key = f"{event_name}:{refund['id']}:{organization_id}:{rec['user_id']}"
            payload_json = Json({
                "refund_id": str(refund["id"]),
                "order_id": str(refund["order_id"]),
                "dispute_id": str(refund["dispute_id"]) if refund["dispute_id"] else None,
                "amount_toman": int(refund["amount_toman"]),
                "status": refund["status"],
                "actor_user_id": actor_user_id,
            })
            cur.execute(
                """
                INSERT INTO outbox_events (
                    id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                    target_user_id,target_organization_id,dedupe_key,channel_hint
                )
                VALUES (
                    gen_random_uuid(),%s,%s,'REFUND',%s,%s,'PENDING',%s,%s,%s,'INBOX'
                )
                ON CONFLICT (event_name,dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
                """,
                (
                    f"{event_name}:{refund['id']}:{rec['user_id']}",
                    event_name,
                    str(refund["id"]),
                    payload_json,
                    rec["user_id"],
                    rec["organization_id"],
                    recipient_key,
                ),
            )
        )

    @classmethod
    def issue_from_dispute(
        cls, cur, actor_user_id, organization_id, dispute_id, amount_toman,
        payment_id=None, reason="", idempotency_key=None, correlation_id=None
    ):
        if not organization_id or not cls._ops_access(cur, actor_user_id, organization_id):
            raise PermissionError("Only active operator staff may issue refunds.")
        if not idempotency_key:
            raise ValueError("Refund issue requires an idempotency key.")
        if amount_toman <= 0:
            raise ValueError("Refund amount must be positive.")

        request_reason = reason.strip()
        base_fingerprint = lambda pid: hashlib.sha256(
            f"{dispute_id}:{amount_toman}:{pid}:{request_reason}".encode()
        ).hexdigest()

        cur.execute(
            """
            SELECT * FROM refunds
            WHERE idempotency_key=%s
            LIMIT 1
            """,
            (idempotency_key,),
        )
        existing = cur.fetchone()
        if existing:
            if str(existing["dispute_id"]) != str(dispute_id):
                raise ValueError("Refund idempotency key is bound to another dispute.")
            existing_fp = existing.get("idempotency_fingerprint")
            if existing_fp and existing_fp != base_fingerprint(existing["payment_id"]):
                raise ValueError("Refund idempotency key was reused with different request data.")
            return dict(existing, idempotent_replay=True)

        cur.execute(
            """
            SELECT d.*,
                   s.id AS settlement_id,
                   s.status AS settlement_status,
                   s.vendor_id AS settlement_vendor_id
            FROM disputes d
            JOIN settlements s ON s.order_id=d.order_id AND s.vendor_id=d.vendor_id
            WHERE d.id=%s
            ORDER BY s.created_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            (dispute_id,),
        )
        dispute = cur.fetchone()
        if not dispute:
            raise KeyError("Dispute not found.")
        if dispute["dispute_status"] != "RESOLVED":
            raise ValueError("Refund can only be issued for a RESOLVED dispute.")
        approved = int(dispute["approved_amount_toman"] or 0)
        if approved <= 0:
            raise ValueError("The resolved dispute has no positive approved refund amount.")
        if amount_toman > approved:
            raise ValueError("Refund amount cannot exceed the approved dispute amount.")

        # Payment provenance: explicit selection is required when more than one
        # successful payment is eligible. Partial prior refunds are subtracted.
        if payment_id:
            cur.execute(
                "SELECT * FROM payments WHERE id=%s AND order_id=%s FOR UPDATE",
                (payment_id, dispute["order_id"]),
            )
        else:
            cur.execute(
                """
                SELECT p.*,
                       p.amount_toman - COALESCE((
                         SELECT SUM(r.amount_toman)
                         FROM refunds r
                         WHERE r.payment_id=p.id
                           AND r.status IN ('PENDING','APPROVED','COMPLETED')
                       ),0) AS refundable_remaining
                FROM payments p
                WHERE p.order_id=%s
                  AND p.retailer_id=%s
                  AND p.vendor_id=%s
                  AND p.payment_status='SUCCESS'
                ORDER BY p.created_at ASC
                FOR UPDATE
                """,
                (dispute["order_id"], dispute["retailer_id"], dispute["vendor_id"]),
            )
            candidates = [dict(x) for x in cur.fetchall()]
            eligible = [x for x in candidates if int(x["refundable_remaining"]) >= amount_toman]
            if len(eligible) != 1:
                raise ValueError("Explicit payment_id is required when refund provenance is ambiguous.")
            payment_id = eligible[0]["id"]
            payment = eligible[0]
        if payment_id and 'payment' not in locals():
            payment = cur.fetchone()

        if not payment:
            raise ValueError("Payment not found for the disputed order.")
        if str(payment["retailer_id"]) != str(dispute["retailer_id"]) or str(payment["vendor_id"]) != str(dispute["vendor_id"]):
            raise PermissionError("Refund payment provenance does not match the disputed retailer/vendor.")
        if payment["payment_status"] != "SUCCESS":
            raise ValueError("Refund requires a successful payment.")
        cur.execute(
            """
            SELECT COALESCE(SUM(amount_toman),0) AS used_amount
            FROM refunds
            WHERE payment_id=%s
              AND status IN ('PENDING','APPROVED','COMPLETED')
            """,
            (payment["id"],),
        )
        used = int(cur.fetchone()["used_amount"])
        if amount_toman > int(payment["amount_toman"]) - used:
            raise ValueError("Refund exceeds the remaining refundable payment amount.")

        cur.execute(
            """
            INSERT INTO refunds
                (id,order_id,payment_id,dispute_id,retailer_id,amount_toman,
                 refund_method,reason,status,created_by_user_id,idempotency_key,idempotency_fingerprint)
            VALUES (%s,%s,%s,%s,%s,%s,'BANK_REVERSAL',%s,'PENDING',%s,%s,%s)
            RETURNING *
            """,
            (
                str(uuid4()), dispute["order_id"], payment["id"], dispute_id,
                dispute["retailer_id"], amount_toman,
                reason.strip() or f"Dispute refund {dispute_id}",
                actor_user_id, idempotency_key, base_fingerprint(payment["id"]),
            ),
        )
        refund = dict(cur.fetchone())
        cls._event(cur, refund, "REFUND_CREATED", actor_user_id, organization_id)
        cls._audit(
            cur, actor_user_id, "REFUND_CREATED", str(refund["id"]), {},
            {"status": "PENDING", "amount_toman": amount_toman,
             "payment_id": str(payment["id"]), "dispute_id": str(dispute_id)},
            reason.strip(), correlation_id,
        )
        return refund

    @classmethod
    def approve(cls, cur, actor_user_id, organization_id, refund_id, reason="", correlation_id=None):
        if not organization_id or not cls._ops_access(cur, actor_user_id, organization_id):
            raise PermissionError("Only active operator staff may approve refunds.")
        cur.execute(
            "SELECT * FROM refunds WHERE id=%s FOR UPDATE",
            (refund_id,),
        )
        refund = cur.fetchone()
        if not refund:
            raise KeyError("Refund not found.")
        if refund["status"] != "PENDING":
            if refund["status"] in ("APPROVED","COMPLETED"):
                return dict(refund, idempotent_replay=True)
            raise ValueError("Only PENDING refunds may be approved.")
        creator = refund.get("created_by_user_id")
        if creator and str(creator) == str(actor_user_id):
            raise PermissionError("Refund approval must be performed by a different actor than the creator.")

        before = {"status": refund["status"], "approved_by_user_id": refund["approved_by_user_id"]}
        cur.execute(
            """
            UPDATE refunds
            SET status='APPROVED', approved_by_user_id=%s, approved_at=now()
            WHERE id=%s AND status='PENDING'
            RETURNING *
            """,
            (actor_user_id, refund_id),
        )
        approved = dict(cur.fetchone())
        cls._event(cur, approved, "REFUND_APPROVED", actor_user_id, organization_id)
        cls._audit(
            cur, actor_user_id, "REFUND_APPROVED", str(refund_id), before,
            {"status": "APPROVED", "approved_by_user_id": str(actor_user_id)},
            reason.strip(), correlation_id,
        )
        return approved

    @classmethod
    def complete(cls, cur, actor_user_id, organization_id, refund_id, reason="", correlation_id=None):
        if not organization_id or not cls._ops_access(cur, actor_user_id, organization_id):
            raise PermissionError("Only active operator staff may complete refunds.")
        cur.execute("SELECT * FROM refunds WHERE id=%s FOR UPDATE", (refund_id,))
        refund = cur.fetchone()
        if not refund:
            raise KeyError("Refund not found.")
        if refund["status"] == "COMPLETED":
            return dict(refund, idempotent_replay=True)
        if refund["status"] != "APPROVED":
            raise ValueError("Only APPROVED refunds may be completed.")
        if str(refund["approved_by_user_id"]) == str(actor_user_id):
            raise PermissionError("Refund completion must be performed by a different actor than the approver.")
        if not refund["payment_id"]:
            raise ValueError("Refund completion requires a linked payment.")

        cur.execute("SELECT * FROM payments WHERE id=%s FOR UPDATE", (refund["payment_id"],))
        payment = cur.fetchone()
        if not payment or payment["payment_status"] != "SUCCESS":
            raise ValueError("Refund completion requires a successful linked payment.")

        cur.execute(
            """
            SELECT s.*
            FROM settlements s
            JOIN orders o ON o.id=s.order_id AND o.vendor_id=s.vendor_id
            WHERE s.order_id=%s
            ORDER BY s.created_at DESC
            LIMIT 1
            FOR UPDATE
            """,
            (refund["order_id"],),
        )
        settlement = cur.fetchone()
        if not settlement:
            raise ValueError("No settlement exists for the refunded order.")
        if settlement["status"] not in ("DISPUTED", "CALCULATED", "RECONCILED"):
            raise ValueError("Refund cannot be completed against a closed or paid-out settlement.")

        # Atomically link this refund to an existing dispute adjustment of the
        # same amount, or create the explicit REFUND adjustment exactly once.
        cur.execute(
            """
            SELECT id, amount_toman
            FROM settlement_adjustments
            WHERE dispute_id=%s
              AND refund_id IS NULL
              AND amount_toman=%s
            ORDER BY created_at ASC
            LIMIT 1
            FOR UPDATE
            """,
            (refund["dispute_id"], refund["amount_toman"]),
        )
        adjustment = cur.fetchone()
        if adjustment:
            cur.execute(
                "UPDATE settlement_adjustments SET refund_id=%s WHERE id=%s",
                (refund_id, adjustment["id"]),
            )
        else:
            cur.execute(
                """
                INSERT INTO settlement_adjustments
                    (id,settlement_id,dispute_id,refund_id,adjustment_type,
                     amount_toman,reason,applied_by_user_id)
                VALUES (%s,%s,%s,%s,'REFUND',%s,%s,%s)
                """,
                (
                    str(uuid4()), settlement["id"], refund["dispute_id"], refund_id,
                    refund["amount_toman"], reason.strip() or "Refund financial adjustment",
                    actor_user_id,
                ),
            )

        cur.execute(
            """
            SELECT COALESCE(SUM(amount_toman),0) AS total
            FROM settlement_adjustments
            WHERE settlement_id=%s
            """,
            (settlement["id"],),
        )
        total_adjustments = int(cur.fetchone()["total"])
        net = int(settlement["gross_amount_toman"]) - int(settlement["commission_amount_toman"]) - total_adjustments

        cur.execute(
            """
            UPDATE settlements
            SET adjustment_amount_toman=-%s,
                net_vendor_amount_toman=%s,
                status='RECONCILED'
            WHERE id=%s
            """,
            (total_adjustments, net, settlement["id"]),
        )

        cur.execute(
            """
            UPDATE refunds
            SET status='COMPLETED', completed_at=now(), completed_by_user_id=%s
            WHERE id=%s AND status='APPROVED'
            RETURNING *
            """,
            (actor_user_id, refund_id),
        )
        completed_row = cur.fetchone()
        if not completed_row:
            raise ValueError("Refund completion raced with another completion request.")
        completed = dict(completed_row)

        cur.execute(
            """
            SELECT COALESCE(SUM(r.amount_toman),0) AS total_completed
            FROM refunds r
            WHERE r.payment_id=%s AND r.status='COMPLETED'
            """,
            (payment["id"],),
        )
        total_completed = int(cur.fetchone()["total_completed"])
        fully_refunded = total_completed == int(payment["amount_toman"])

        if fully_refunded:
            cur.execute(
                """
                UPDATE payments
                SET payment_status='REFUNDED'
                WHERE id=%s AND payment_status='SUCCESS'
                """,
                (payment["id"],),
            )
            if cur.rowcount != 1:
                raise ValueError("Linked payment is no longer refundable.")

        cls._event(cur, completed, "REFUND_COMPLETED", actor_user_id, organization_id)
        if fully_refunded:
            cls._event(cur, completed, "PAYMENT_REFUNDED", actor_user_id, organization_id)

        if refund["dispute_id"]:
            cur.execute(
                """
                SELECT dispute_status, resolution_outcome, order_id
                FROM disputes WHERE id=%s FOR UPDATE
                """,
                (refund["dispute_id"],),
            )
            dispute = cur.fetchone()
            if dispute and dispute["dispute_status"] == "RESOLVED":
                cur.execute(
                    """
                    UPDATE disputes
                    SET dispute_status='CLOSED', closed_at=now()
                    WHERE id=%s
                    """,
                    (refund["dispute_id"],),
                )
                cur.execute(
                    "UPDATE orders SET dispute_status='CLOSED', updated_at=now() WHERE id=%s",
                    (dispute["order_id"],),
                )
                cur.execute(
                    """
                    INSERT INTO dispute_events
                        (dispute_id,from_status,to_status,actor_user_id,reason,event_data)
                    VALUES (%s,'RESOLVED','CLOSED',%s,%s,%s)
                    """,
                    (
                        refund["dispute_id"], actor_user_id,
                        reason.strip() or "Refund completed",
                        Json({"refund_id": str(refund_id)}),
                    ),
                )

        cls._audit(
            cur, actor_user_id, "REFUND_COMPLETED", str(refund_id),
            {"status": "APPROVED", "payment_id": str(payment["id"])},
            {"status": "COMPLETED", "payment_status": "REFUNDED",
             "amount_toman": int(completed["amount_toman"])},
            reason.strip(), correlation_id,
        )
        return completed

    @classmethod
    def get(cls, cur, actor_user_id, organization_id, refund_id):
        if not organization_id or not cls._ops_access(cur, actor_user_id, organization_id):
            raise PermissionError("Only active operator staff may read refunds.")
        cur.execute(
            """
            SELECT r.*
            FROM refunds r
            WHERE r.id=%s
            """,
            (refund_id,),
        )
        refund = cur.fetchone()
        if not refund:
            raise KeyError("Refund not found.")
        return dict(refund)

    @classmethod
    def list(cls, cur, actor_user_id, organization_id, limit=50, offset=0):
        if not organization_id or not cls._ops_access(cur, actor_user_id, organization_id):
            raise PermissionError("Only active operator staff may list refunds.")
        cur.execute(
            """
            SELECT r.*
            FROM refunds r
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        return {"refunds": [dict(r) for r in cur.fetchall()], "limit": limit, "offset": offset}
