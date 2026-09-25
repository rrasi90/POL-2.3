"""Canonical Fulfillment Service — Stage 22.

Implements the PREPARING → READY → DISPATCHED → DELIVERED state machine
for vendor fulfillment operations. Replaces the dead FulfillmentService stubs
in domain_services.py.

FastAPI architecture: this module is imported by application_boundary.py only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4, uuid5, NAMESPACE_URL

from scripts.operational_config import OTP_CODE_LENGTH
from scripts.operational_policies import AllocationIntegrityError

VALID_FULFILLMENT_TRANSITIONS = {
    "ACCEPTED": {"PREPARING"},
    "PARTIALLY_ACCEPTED": {"PREPARING"},
    "PREPARING": {"READY", "CANCELLED"},
    "READY": {"DISPATCHED", "CANCELLED"},
}

VALID_DISPATCH_TRANSITIONS = {"READY"}
VALID_DELIVERY_TRANSITIONS = {"DISPATCHED"}


def _guard_transition(cur, order_id, expected_from: set[str]) -> dict:
    cur.execute(
        "SELECT o.id, o.order_status, o.vendor_id, o.retailer_id, o.order_number, "
        "r.organization_id AS retailer_organization_id "
        "FROM orders o "
        "JOIN retailers r ON r.id=o.retailer_id "
        "WHERE o.id = %s FOR UPDATE",
        (order_id,),
    )
    order = cur.fetchone()
    if not order:
        raise ValueError("Order not found.")
    order = dict(order)
    if order["order_status"] not in expected_from:
        raise AllocationIntegrityError(
            f"Cannot transition from {order['order_status']}. "
            f"Expected one of: {sorted(expected_from)}"
        )
    return order


def _emit_outbox(cur, *, event_name, aggregate_id, aggregate_type, payload, recipient_org_id):
    """Create one durable, deterministically deduplicated event per active commercial recipient."""
    cur.execute(
        """
        SELECT om.user_id, om.organization_id
        FROM organization_memberships om
        JOIN organizations o ON o.id = om.organization_id
        WHERE om.organization_id = %s
          AND om.status = 'ACTIVE'
          AND o.status = 'ACTIVE'
          AND om.role IN ('RETAILER_OWNER', 'RETAILER_STAFF', 'VENDOR_OWNER', 'VENDOR_STAFF')
        ORDER BY om.user_id
        """,
        (recipient_org_id,),
    )
    recipients = cur.fetchall()
    if not recipients:
        raise ValueError("Notification target organization has no active commercial recipient.")

    for recipient in recipients:
        dedupe_key = (
            f"{event_name}:{aggregate_type}:{aggregate_id}:"
            f"{recipient['organization_id']}:{recipient['user_id']}"
        )
        event_id = str(uuid5(NAMESPACE_URL, dedupe_key))
        cur.execute(
            """
            INSERT INTO outbox_events (
                id, event_id, event_name, aggregate_type, aggregate_id, payload,
                status, target_user_id, target_organization_id, dedupe_key, channel_hint, created_at
            )
            VALUES (
                gen_random_uuid(), %s, %s, %s, %s, %s::jsonb,
                'PENDING', %s, %s, %s, 'INBOX', now()
            )
            ON CONFLICT (event_name, dedupe_key)
            WHERE dedupe_key IS NOT NULL
            DO NOTHING
            """,
            (
                event_id,
                event_name,
                aggregate_type,
                aggregate_id,
                json_dumps(payload),
                recipient["user_id"],
                recipient["organization_id"],
                dedupe_key,
            ),
        )

def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, uuid4().__class__):
        return str(obj)
    return str(obj)


def json_dumps(obj):
    import json
    return json.dumps(obj, default=_json_default, ensure_ascii=False)


def mark_preparing(cur, *, user_id, organization_id, order_id) -> dict:
    """Transition ACCEPTED/PARTIALLY_ACCEPTED → PREPARING."""
    order = _guard_transition(cur, order_id, {
        "ACCEPTED", "PARTIALLY_ACCEPTED", "PREPARING"
    })
    _verify_vendor_actor(cur, user_id, organization_id, order["vendor_id"])
    if order["order_status"] == "PREPARING":
        return {
            "order_id": order_id,
            "order_status": "PREPARING",
            "previous_status": "PREPARING",
            "idempotent_replay": True,
        }

    cur.execute(
        "UPDATE orders SET order_status = 'PREPARING', updated_at = now() WHERE id = %s",
        (order_id,),
    )
    _record_timeline(cur, order_id, order["order_status"], "PREPARING", user_id, organization_id)
    _emit_outbox(
        cur,
        event_name="ORDER_PREPARING",
        aggregate_id=order_id,
        aggregate_type="ORDER",
        payload={
            "order_id": order_id,
            "order_number": order["order_number"],
            "order_status": "PREPARING",
        },
        recipient_org_id=order["retailer_organization_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "PREPARING",
        "previous_status": order["order_status"],
    }


def mark_ready(cur, *, user_id, organization_id, order_id) -> dict:
    """Transition PREPARING → READY."""
    order = _guard_transition(cur, order_id, {"PREPARING", "READY"})
    _verify_vendor_actor(cur, user_id, organization_id, order["vendor_id"])
    if order["order_status"] == "READY":
        return {
            "order_id": order_id,
            "order_status": "READY",
            "previous_status": "READY",
            "idempotent_replay": True,
        }

    cur.execute(
        "UPDATE orders SET order_status = 'READY', updated_at = now() WHERE id = %s",
        (order_id,),
    )
    _record_timeline(cur, order_id, "PREPARING", "READY", user_id, organization_id)
    _emit_outbox(
        cur,
        event_name="ORDER_READY",
        aggregate_id=order_id,
        aggregate_type="ORDER",
        payload={
            "order_id": order_id,
            "order_number": order["order_number"],
            "order_status": "READY",
        },
        recipient_org_id=order["retailer_organization_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "READY",
        "previous_status": "PREPARING",
    }


def dispatch_order(cur, *, user_id, organization_id, order_id, driver_name=None,
                   vehicle_plate=None, driver_phone=None) -> dict:
    """Transition READY → DISPATCHED. Creates an ASSIGNED delivery record."""
    order = _guard_transition(cur, order_id, {"READY", "DISPATCHED"})
    _verify_vendor_actor(cur, user_id, organization_id, order["vendor_id"])

    if order["order_status"] == "DISPATCHED":
        cur.execute(
            """
            SELECT id, delivery_status, driver_name, vehicle_plate, driver_phone
            FROM deliveries
            WHERE order_id=%s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (order_id,),
        )
        delivery = cur.fetchone()
        if not delivery:
            raise ValueError("Order is DISPATCHED but has no delivery record.")
        return {
            "order_id": order_id,
            "order_status": "DISPATCHED",
            "delivery_id": str(delivery["id"]),
            "delivery_otp": None,
            "delivery_status": delivery["delivery_status"],
            "idempotent_replay": True,
        }

    required = {
        "driver_name": (driver_name or "").strip(),
        "vehicle_plate": (vehicle_plate or "").strip(),
        "driver_phone": (driver_phone or "").strip(),
    }
    if any(not value for value in required.values()):
        raise ValueError("driver_name, driver_phone and vehicle_plate are required for dispatch.")

    delivery_id = str(uuid4())
    otp = f"{uuid4().int % (10 ** OTP_CODE_LENGTH):0{OTP_CODE_LENGTH}d}"
    cur.execute(
        """
        INSERT INTO deliveries (
            id, order_id, vendor_id, delivery_status, driver_name, vehicle_plate,
            driver_phone, delivery_otp, assigned_at, created_at
        )
        VALUES (%s, %s, %s, 'ASSIGNED', %s, %s, %s, %s, now(), now())
        """,
        (delivery_id, order_id, order["vendor_id"], required["driver_name"],
         required["vehicle_plate"], required["driver_phone"], otp),
    )
    cur.execute(
        """
        INSERT INTO outbox_events (
            id, event_id, event_name, aggregate_type, aggregate_id, payload,
            status, target_user_id, target_organization_id, dedupe_key, channel_hint, created_at
        )
        SELECT gen_random_uuid(), %s, 'DELIVERY_OTP_GENERATED', 'DELIVERY', %s,
               %s::jsonb, 'PENDING', om.user_id, om.organization_id, %s, 'INBOX', now()
        FROM organization_memberships om
        WHERE om.organization_id = (
            SELECT r.organization_id FROM retailers r WHERE r.id = %s
        )
          AND om.status='ACTIVE'
          AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
        ON CONFLICT (event_name, dedupe_key)
        WHERE dedupe_key IS NOT NULL
        DO NOTHING
        """,
        (
            str(uuid5(NAMESPACE_URL, f"DELIVERY_OTP_GENERATED:{delivery_id}")),
            delivery_id,
            json_dumps({"delivery_id": delivery_id, "order_id": order_id}),
            f"DELIVERY_OTP_GENERATED:{delivery_id}",
            order["retailer_id"],
        ),
    )
    cur.execute(
        "UPDATE orders SET order_status = 'DISPATCHED', updated_at = now() WHERE id = %s",
        (order_id,),
    )
    _record_timeline(cur, order_id, "READY", "DISPATCHED", user_id, organization_id,
                     {"delivery_id": delivery_id, "delivery_status": "ASSIGNED"})
    _emit_outbox(
        cur,
        event_name="ORDER_DISPATCHED",
        aggregate_id=order_id,
        aggregate_type="ORDER",
        payload={
            "order_id": order_id,
            "order_number": order["order_number"],
            "order_status": "DISPATCHED",
            "delivery_id": delivery_id,
        },
        recipient_org_id=order["retailer_organization_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "DISPATCHED",
        "delivery_id": delivery_id,
        "delivery_otp": otp,
        "delivery_status": "ASSIGNED",
        "idempotent_replay": False,
    }


def confirm_delivery(cur, *, user_id, organization_id, order_id, recipient_name=None,
                     otp_code=None, proof_type="OTP_CODE", proof_media_id=None,
                     issue_reported=None) -> dict:
    """Transition active delivery to DELIVERED with mandatory one-time OTP verification."""
    order = _guard_transition(cur, order_id, {"DISPATCHED", "DELIVERED"})
    _verify_retailer_actor(cur, user_id, organization_id, order["retailer_id"])

    if order["order_status"] == "DELIVERED":
        cur.execute(
            """
            SELECT d.id, d.delivery_status, pod.accepted_by_name, pod.accepted_at,
                   pod.otp_verified, pod.proof_type
            FROM deliveries d
            LEFT JOIN proof_of_delivery pod ON pod.delivery_id=d.id
            WHERE d.order_id=%s
            ORDER BY d.created_at DESC
            LIMIT 1
            """,
            (order_id,),
        )
        delivery = cur.fetchone()
        return {
            "order_id": order_id,
            "order_status": "DELIVERED",
            "delivery_id": str(delivery["id"]) if delivery else None,
            "otp_verified": bool(delivery["otp_verified"]) if delivery else True,
            "idempotent_replay": True,
        }

    if not recipient_name or not str(recipient_name).strip():
        raise ValueError("recipient_name is required for proof of delivery.")
    if not otp_code:
        raise ValueError("Delivery OTP is required.")

    cur.execute(
        """
        SELECT id, delivery_status, delivery_otp, delivery_otp_used_at,
               delivery_otp_attempt_count, delivery_otp_expires_at
        FROM deliveries
        WHERE order_id=%s
          AND delivery_status IN ('ASSIGNED','PICKED_UP','IN_TRANSIT','ARRIVED')
        ORDER BY created_at DESC
        LIMIT 1
        FOR UPDATE
        """,
        (order_id,),
    )
    delivery = cur.fetchone()
    if not delivery:
        raise ValueError("No active delivery found for this order.")

    delivery_id = str(delivery["id"])

    if delivery["delivery_otp_used_at"] is not None:
        raise ValueError("Delivery OTP has already been used.")

    if delivery["delivery_otp_expires_at"] is not None:
        cur.execute("SELECT now() >= %s AS expired", (delivery["delivery_otp_expires_at"],))
        if cur.fetchone()["expired"]:
            raise ValueError("Delivery OTP has expired.")

    cur.execute(
        """
        UPDATE deliveries
        SET delivery_otp_attempt_count = delivery_otp_attempt_count + 1,
            last_otp_attempt_at = now()
        WHERE id=%s
        """,
        (delivery_id,),
    )

    if str(delivery["delivery_otp"]) != str(otp_code):
        raise ValueError("Invalid delivery OTP.")

    # OTP is consumed atomically before the terminal mutation.
    cur.execute(
        """
        UPDATE deliveries
        SET delivery_otp_used_at = now()
        WHERE id=%s AND delivery_otp_used_at IS NULL
        """,
        (delivery_id,),
    )
    if cur.rowcount != 1:
        raise ValueError("Delivery OTP has already been used.")

    cur.execute(
        """
        UPDATE deliveries
        SET delivery_status='DELIVERED', delivered_at=now()
        WHERE id=%s
        """,
        (delivery_id,),
    )

    cur.execute(
        """
        INSERT INTO proof_of_delivery (
            id, delivery_id, accepted_by_name, accepted_at,
            proof_type, otp_verified, proof_media_id, issue_reported_at_delivery
        )
        VALUES (%s, %s, %s, now(), 'OTP_CODE', TRUE, %s, %s IS NOT NULL)
        """,
        (str(uuid4()), delivery_id, recipient_name, proof_media_id, issue_reported),
    )

    cur.execute(
        """
        SELECT id, ordered_quantity, accepted_quantity, delivered_quantity, fulfillment_status
        FROM order_items
        WHERE order_id=%s
        FOR UPDATE
        """,
        (order_id,),
    )
    items = cur.fetchall()
    if not items:
        raise ValueError("Delivered order has no order items.")

    for item in items:
        accepted = int(item["accepted_quantity"] or item["ordered_quantity"])
        status = "SHORTAGE" if accepted < int(item["ordered_quantity"]) else "FULFILLED"
        cur.execute(
            """
            UPDATE order_items
            SET delivered_quantity=%s, fulfillment_status=%s
            WHERE id=%s
            """,
            (accepted, status, item["id"]),
        )

    cur.execute(
        "UPDATE orders SET order_status='DELIVERED', updated_at=now() WHERE id=%s",
        (order_id,),
    )
    _record_timeline(
        cur, order_id, "DISPATCHED", "DELIVERED", user_id, organization_id,
        {"delivery_id": delivery_id, "recipient_name": recipient_name, "otp_verified": True,
         "proof_type": "OTP_CODE"},
    )
    _emit_outbox(
        cur,
        event_name="ORDER_DELIVERED",
        aggregate_id=order_id,
        aggregate_type="ORDER",
        payload={
            "order_id": order_id,
            "order_number": order["order_number"],
            "order_status": "DELIVERED",
            "delivery_id": delivery_id,
            "otp_verified": True,
        },
        recipient_org_id=order["retailer_organization_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "DELIVERED",
        "delivery_id": delivery_id,
        "otp_verified": True,
        "idempotent_replay": False,
    }

def _verify_vendor_actor(cur, user_id, organization_id, vendor_id):
    cur.execute(
        """
        SELECT 1
        FROM vendors v
        JOIN organization_memberships om ON om.organization_id=v.organization_id
        WHERE v.id=%s
          AND v.organization_id=%s
          AND om.user_id=%s
          AND om.status='ACTIVE'
          AND om.role IN ('VENDOR_OWNER','VENDOR_STAFF')
        """,
        (vendor_id, organization_id, user_id),
    )
    if not cur.fetchone():
        raise PermissionError("Actor is not authorized for this vendor.")


def _verify_retailer_actor(cur, user_id, organization_id, retailer_id):
    cur.execute(
        """
        SELECT 1
        FROM retailers r
        JOIN organization_memberships om ON om.organization_id=r.organization_id
        WHERE r.id=%s
          AND r.organization_id=%s
          AND om.user_id=%s
          AND om.status='ACTIVE'
          AND om.role IN ('RETAILER_OWNER','RETAILER_STAFF')
        """,
        (retailer_id, organization_id, user_id),
    )
    if not cur.fetchone():
        raise PermissionError("Actor is not authorized for this retailer.")


def _record_timeline(cur, order_id, from_status, to_status, actor_user_id,
                     actor_organization_id, event_data=None):
    import json as _json
    cur.execute(
        "INSERT INTO order_timeline_events "
        "(order_id, event_type, from_status, to_status, actor_user_id, actor_organization_id, event_data) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            order_id,
            f"{from_status}_TO_{to_status}" if from_status else to_status,
            from_status,
            to_status,
            actor_user_id,
            actor_organization_id,
            _json.dumps(event_data or {}, default=str),
        ),
    )
