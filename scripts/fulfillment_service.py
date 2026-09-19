"""Canonical Fulfillment Service — Stage 22.

Implements the PREPARING → READY → DISPATCHED → DELIVERED state machine
for vendor fulfillment operations. Replaces the dead FulfillmentService stubs
in domain_services.py.

FastAPI architecture: this module is imported by application_boundary.py only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

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
        "SELECT id, order_status, vendor_id, retailer_id, order_number "
        "FROM orders WHERE id = %s",
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
    cur.execute(
        "INSERT INTO outbox_events (id, event_id, event_name, aggregate_type, aggregate_id, payload, status, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, 'PENDING', now())",
        (str(uuid4()), str(uuid4()), event_name, aggregate_type, aggregate_id, json_dumps(payload)),
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
    order = _guard_transition(cur, order_id, {"ACCEPTED", "PARTIALLY_ACCEPTED"})
    _verify_vendor_actor(cur, user_id, organization_id, order["vendor_id"])

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
        recipient_org_id=order["retailer_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "PREPARING",
        "previous_status": order["order_status"],
    }


def mark_ready(cur, *, user_id, organization_id, order_id) -> dict:
    """Transition PREPARING → READY."""
    order = _guard_transition(cur, order_id, {"PREPARING"})
    _verify_vendor_actor(cur, user_id, organization_id, order["vendor_id"])

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
        recipient_org_id=order["retailer_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "READY",
        "previous_status": "PREPARING",
    }


def dispatch_order(cur, *, user_id, organization_id, order_id, driver_name=None,
                   vehicle_plate=None, driver_phone=None) -> dict:
    """Transition READY → DISPATCHED. Creates delivery record."""
    order = _guard_transition(cur, order_id, {"READY"})
    _verify_vendor_actor(cur, user_id, organization_id, order["vendor_id"])

    delivery_id = str(uuid4())
    otp = f"{uuid4().int % 1000000:06d}"
    cur.execute(
        "INSERT INTO deliveries (id, order_id, vendor_id, delivery_status, driver_name, vehicle_plate, driver_phone, dispatched_at, created_at) "
        "VALUES (%s, %s, %s, 'IN_TRANSIT', %s, %s, %s, now(), now())",
        (delivery_id, order_id, order["vendor_id"], driver_name, vehicle_plate, driver_phone),
    )
    cur.execute(
        "UPDATE orders SET order_status = 'DISPATCHED', updated_at = now() WHERE id = %s",
        (order_id,),
    )
    _record_timeline(cur, order_id, "READY", "DISPATCHED", user_id, organization_id,
                     {"delivery_id": delivery_id})
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
        recipient_org_id=order["retailer_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "DISPATCHED",
        "delivery_id": delivery_id,
        "delivery_otp": otp,
    }


def confirm_delivery(cur, *, user_id, organization_id, order_id, recipient_name=None,
                     otp_code=None, proof_type="OTP_CODE", proof_media_id=None,
                     issue_reported=None) -> dict:
    """Transition DISPATCHED → DELIVERED. Creates proof of delivery with optional OTP verification.
    Only the retailer (recipient) can confirm delivery."""
    order = _guard_transition(cur, order_id, {"DISPATCHED"})
    _verify_retailer_actor(cur, user_id, organization_id, order["retailer_id"])

    cur.execute(
        "SELECT id, driver_name FROM deliveries WHERE order_id = %s AND delivery_status = 'IN_TRANSIT' LIMIT 1",
        (order_id,),
    )
    delivery = cur.fetchone()
    if not delivery:
        raise ValueError("No active delivery found for this order.")
    delivery_id = str(delivery["id"])

    otp_verified = False
    if otp_code:
        cur.execute(
            "SELECT 1 FROM deliveries WHERE id = %s AND delivery_otp = %s",
            (delivery_id, otp_code),
        )
        otp_verified = cur.fetchone() is not None

    cur.execute(
        "UPDATE deliveries SET delivery_status = 'DELIVERED', delivered_at = now() WHERE id = %s",
        (delivery_id,),
    )
    cur.execute(
        "INSERT INTO proof_of_delivery (id, delivery_id, accepted_by_name, accepted_at, "
        "proof_type, otp_verified, proof_media_id, issue_reported_at_delivery) "
        "VALUES (%s, %s, %s, now(), %s, %s, %s, %s IS NOT NULL)",
        (str(uuid4()), delivery_id, recipient_name, proof_type, otp_verified,
         proof_media_id, issue_reported),
    )
    cur.execute(
        "UPDATE orders SET order_status = 'DELIVERED', updated_at = now() WHERE id = %s",
        (order_id,),
    )
    _record_timeline(cur, order_id, "DISPATCHED", "DELIVERED", user_id, organization_id,
                     {"delivery_id": delivery_id, "recipient_name": recipient_name,
                      "otp_verified": otp_verified, "proof_type": proof_type})
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
            "otp_verified": otp_verified,
        },
        recipient_org_id=order["retailer_id"],
    )
    return {
        "order_id": order_id,
        "order_status": "DELIVERED",
        "delivery_id": delivery_id,
        "otp_verified": otp_verified,
    }


def _verify_vendor_actor(cur, user_id, organization_id, vendor_id):
    cur.execute(
        "SELECT 1 FROM vendors WHERE id = %s AND organization_id = %s",
        (vendor_id, organization_id),
    )
    if not cur.fetchone():
        raise PermissionError("Actor is not authorized for this vendor.")


def _verify_retailer_actor(cur, user_id, organization_id, retailer_id):
    cur.execute(
        "SELECT 1 FROM retailers WHERE id = %s AND organization_id = %s",
        (retailer_id, organization_id),
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
