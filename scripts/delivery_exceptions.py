"""Canonical Delivery Exceptions Service — Stage 25.

Implements delivery-time exception lifecycle: report → review → resolve.
Links to existing returns/disputes infrastructure.

FastAPI architecture: this module is imported by application_boundary.py only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from scripts.operational_policies import AllocationIntegrityError


VALID_EXCEPTION_TYPES = {
    "DOORSTEP_REJECTION", "DAMAGED_GOODS", "ITEM_DISCREPANCY",
    "INCOMPLETE_DELIVERY", "VENDOR_NO_SHOW", "QUALITY_ISSUE", "OTHER",
}

VALID_RESOLUTION_TYPES = {
    "FULL_REFUND", "PARTIAL_REFUND", "REPLACEMENT",
    "NO_ACTION", "RETURN_PICKUP", "ESCALATED_TO_OPS",
}

EXCEPTION_TRANSITIONS = {
    "REPORTED": {"UNDER_REVIEW", "RESOLVED", "ESCALATED", "CANCELLED"},
    "UNDER_REVIEW": {"RESOLVED", "ESCALATED", "CANCELLED"},
    "RESOLVED": set(),
    "ESCALATED": {"RESOLVED", "CANCELLED"},
    "CANCELLED": set(),
}


def _json_dumps(obj):
    import json
    from datetime import datetime as _dt
    from uuid import UUID as _UUID
    def _default(o):
        if isinstance(o, _dt):
            return o.isoformat()
        if isinstance(o, _UUID):
            return str(o)
        return str(o)
    return json.dumps(obj, default=_default, ensure_ascii=False)


def report_delivery_exception(
    cur, *, user_id, organization_id, delivery_id, order_id,
    exception_type, description=None,
) -> dict:
    """Retailer reports a delivery exception at doorstep or post-delivery."""
    if exception_type not in VALID_EXCEPTION_TYPES:
        raise ValueError(f"Invalid exception_type: {exception_type}. Must be one of: {sorted(VALID_EXCEPTION_TYPES)}")

    cur.execute(
        "SELECT id, order_status, vendor_id, retailer_id FROM orders WHERE id = %s",
        (order_id,),
    )
    order = cur.fetchone()
    if not order:
        raise ValueError("Order not found.")
    order = dict(order)

    cur.execute(
        "SELECT id, delivery_status FROM deliveries WHERE id = %s AND order_id = %s",
        (delivery_id, order_id),
    )
    delivery = cur.fetchone()
    if not delivery:
        raise ValueError("Delivery not found for this order.")
    delivery = dict(delivery)

    _verify_retailer_access(cur, user_id, organization_id, order["retailer_id"])

    cur.execute("SELECT 1 FROM delivery_exceptions WHERE delivery_id = %s AND status IN ('REPORTED', 'UNDER_REVIEW')", (delivery_id,))
    if cur.fetchone():
        raise AllocationIntegrityError("An open exception already exists for this delivery.")

    exception_id = str(uuid4())
    cur.execute(
        "INSERT INTO delivery_exceptions "
        "(id, delivery_id, order_id, retailer_id, vendor_id, exception_type, status, description, reported_by_user_id, reported_at, created_at, updated_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, 'REPORTED', %s, %s, now(), now(), now())",
        (exception_id, delivery_id, order_id, order["retailer_id"],
         order["vendor_id"], exception_type, description, user_id),
    )

    _record_exception_event(cur, order_id, None, "REPORTED", user_id, organization_id,
                            {"exception_id": exception_id, "exception_type": exception_type,
                             "description": description, "delivery_id": delivery_id})
    _emit_exception_outbox(cur, "DELIVERY_EXCEPTION_REPORTED", exception_id,
                           {"order_id": order_id, "delivery_id": delivery_id,
                            "exception_type": exception_type})

    return {
        "exception_id": exception_id,
        "status": "REPORTED",
        "exception_type": exception_type,
        "order_id": order_id,
        "delivery_id": delivery_id,
    }


def resolve_delivery_exception(
    cur, *, user_id, organization_id, exception_id,
    resolution_type, resolution_note=None,
) -> dict:
    """Vendor or ops resolves an open delivery exception."""
    if resolution_type not in VALID_RESOLUTION_TYPES:
        raise ValueError(f"Invalid resolution_type: {resolution_type}. Must be one of: {sorted(VALID_RESOLUTION_TYPES)}")

    cur.execute(
        "SELECT id, status, order_id, delivery_id, vendor_id, retailer_id, exception_type "
        "FROM delivery_exceptions WHERE id = %s",
        (exception_id,),
    )
    exc = cur.fetchone()
    if not exc:
        raise ValueError("Delivery exception not found.")
    exc = dict(exc)

    if exc["status"] not in ("REPORTED", "UNDER_REVIEW", "ESCALATED"):
        raise AllocationIntegrityError(
            f"Cannot resolve exception in status '{exc['status']}'. Must be REPORTED, UNDER_REVIEW, or ESCALATED."
        )

    cur.execute(
        "UPDATE delivery_exceptions SET status = 'RESOLVED', resolution_type = %s, "
        "resolution_note = %s, resolved_at = now(), updated_at = now() WHERE id = %s",
        (resolution_type, resolution_note, exception_id),
    )

    _record_exception_event(cur, exc["order_id"], exc["status"], "RESOLVED", user_id, organization_id,
                            {"exception_id": exception_id, "resolution_type": resolution_type,
                             "resolution_note": resolution_note})
    _emit_exception_outbox(cur, "DELIVERY_EXCEPTION_RESOLVED", exception_id,
                           {"order_id": exc["order_id"], "delivery_id": exc["delivery_id"],
                            "exception_type": exc["exception_type"], "resolution_type": resolution_type})

    return {
        "exception_id": exception_id,
        "status": "RESOLVED",
        "resolution_type": resolution_type,
    }


def escalate_delivery_exception(
    cur, *, user_id, organization_id, exception_id, reason=None,
) -> dict:
    """Escalate a delivery exception to ops for manual resolution."""
    cur.execute(
        "SELECT id, status, order_id, delivery_id FROM delivery_exceptions WHERE id = %s",
        (exception_id,),
    )
    exc = cur.fetchone()
    if not exc:
        raise ValueError("Delivery exception not found.")
    exc = dict(exc)

    if exc["status"] not in ("REPORTED", "UNDER_REVIEW"):
        raise AllocationIntegrityError(
            f"Cannot escalate exception in status '{exc['status']}'. Must be REPORTED or UNDER_REVIEW."
        )

    cur.execute(
        "UPDATE delivery_exceptions SET status = 'ESCALATED', resolution_type = 'ESCALATED_TO_OPS', "
        "resolution_note = %s, updated_at = now() WHERE id = %s",
        (reason, exception_id),
    )

    _record_exception_event(cur, exc["order_id"], exc["status"], "ESCALATED", user_id, organization_id,
                            {"exception_id": exception_id, "reason": reason})
    _emit_exception_outbox(cur, "DELIVERY_EXCEPTION_ESCALATED", exception_id,
                           {"order_id": exc["order_id"], "delivery_id": exc["delivery_id"]})

    return {"exception_id": exception_id, "status": "ESCALATED"}


def list_delivery_exceptions(cur, *, order_id=None, delivery_id=None, status=None,
                             offset=0, limit=50) -> list[dict]:
    """Query delivery exceptions with optional filters."""
    where_clauses = []
    params = []
    if order_id:
        where_clauses.append("de.order_id = %s")
        params.append(order_id)
    if delivery_id:
        where_clauses.append("de.delivery_id = %s")
        params.append(delivery_id)
    if status:
        where_clauses.append("de.status = %s")
        params.append(status)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    cur.execute(
        f"SELECT de.id, de.delivery_id, de.order_id, de.exception_type, de.status, "
        f"de.description, de.resolution_type, de.resolution_note, de.reported_at, de.resolved_at, "
        f"de.created_at "
        f"FROM delivery_exceptions de "
        f"WHERE {where_sql} "
        f"ORDER BY de.reported_at DESC "
        f"LIMIT %s OFFSET %s",
        (*params, limit, offset),
    )
    return [dict(r) for r in cur.fetchall()]


def get_delivery_exception(cur, *, exception_id) -> dict | None:
    """Get a single delivery exception by ID."""
    cur.execute(
        "SELECT id, delivery_id, order_id, retailer_id, vendor_id, exception_type, "
        "status, description, resolution_type, resolution_note, "
        "reported_by_user_id, reported_at, resolved_at, created_at, updated_at "
        "FROM delivery_exceptions WHERE id = %s",
        (exception_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None


def _verify_retailer_access(cur, user_id, organization_id, retailer_id):
    cur.execute(
        "SELECT 1 FROM retailers WHERE id = %s AND organization_id = %s",
        (retailer_id, organization_id),
    )
    if not cur.fetchone():
        raise PermissionError("Actor is not authorized for this retailer.")


def _record_exception_event(cur, exception_id, from_status, to_status,
                            actor_user_id, actor_organization_id, event_data=None):
    import json as _json
    cur.execute(
        "INSERT INTO order_timeline_events "
        "(order_id, event_type, from_status, to_status, actor_user_id, actor_organization_id, event_data) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (
            exception_id,
            f"EXCEPTION_{from_status}_TO_{to_status}" if from_status else f"EXCEPTION_{to_status}",
            from_status,
            to_status,
            actor_user_id,
            actor_organization_id,
            _json.dumps(event_data or {}, default=str),
        ),
    )


def _emit_exception_outbox(
    cur,
    event_name,
    exception_id,
    payload,
    *,
    recipient_org_id=None,
    recipient_roles=(),
    operator_orgs=False,
):
    clauses = ["m.status='ACTIVE'", "u.is_active=TRUE"]
    params = []
    if operator_orgs:
        clauses.append("o.org_type='OPERATOR'")
    elif recipient_org_id:
        clauses.append("m.organization_id=%s")
        params.append(recipient_org_id)
    else:
        raise ValueError("A notification target organization is required.")
    if recipient_roles:
        clauses.append("m.role = ANY(%s)")
        params.append(list(recipient_roles))
    where_sql = " AND ".join(clauses)
    cur.execute(
        f"""
        SELECT m.user_id, m.organization_id
        FROM organization_memberships m
        JOIN users u ON u.id=m.user_id
        JOIN organizations o ON o.id=m.organization_id
        WHERE {where_sql}
        ORDER BY m.organization_id, m.user_id
        """,
        tuple(params),
    )
    recipients = cur.fetchall()
    if not recipients:
        raise ValueError("Delivery exception notification has no active recipient.")

    for recipient in recipients:
        dedupe_key = f"{event_name}:{exception_id}:{recipient['organization_id']}:{recipient['user_id']}"
        cur.execute(
            """
            INSERT INTO outbox_events (
                id, event_id, event_name, aggregate_type, aggregate_id, payload, status,
                target_user_id, target_organization_id, dedupe_key, channel_hint, created_at
            )
            VALUES (
                %s, %s, %s, 'DELIVERY_EXCEPTION', %s, %s, 'PENDING',
                %s, %s, %s, 'INBOX', now()
            )
            ON CONFLICT (event_name, dedupe_key) WHERE dedupe_key IS NOT NULL DO NOTHING
            """,
            (
                str(uuid4()),
                str(uuid4()),
                event_name,
                exception_id,
                _json_dumps(payload),
                str(recipient["user_id"]),
                str(recipient["organization_id"]),
                dedupe_key,
            ),
        )
    )
