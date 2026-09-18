"""PostgreSQL integration tests for the two-party partial acceptance contract."""

from __future__ import annotations

import pytest
from psycopg2.extras import RealDictCursor
from uuid import uuid4

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.test_vendor_order_acceptance import _setup_order


def _vendor_boundary(cur, data):
    return POLApplicationBoundary(
        cur,
        ApplicationContext(
            user_id=data["vendor_user"],
            organization_id=data["vendor_org"],
            correlation_id=f"partial-vendor-{uuid4()}",
        ),
    )


def _retailer_boundary(cur, data):
    return POLApplicationBoundary(
        cur,
        ApplicationContext(
            user_id=data["retailer_user"],
            organization_id=data["retailer_org"],
            correlation_id=f"partial-retailer-{uuid4()}",
        ),
    )


def _propose(cur, data, accepted_quantity=7, reason="SHORTAGE"):
    return _vendor_boundary(cur, data).vendor_partial_acceptance_propose(
        order_id=data["order_id"],
        idempotency_key=str(uuid4()),
        items=[
            {
                "order_item_id": data["order_item_id"],
                "accepted_quantity": accepted_quantity,
                "reason": reason,
            }
        ],
    )


def test_vendor_partial_proposal_does_not_mutate_order_or_inventory(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            result = _propose(cur, data)
            assert result["status"] == "PENDING"

            cur.execute(
                "SELECT order_status, total_amount_toman FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            order = cur.fetchone()
            assert order["order_status"] == "SUBMITTED"
            assert order["total_amount_toman"] == 5000000

            cur.execute(
                "SELECT status, consumed_quantity FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            reservation = cur.fetchone()
            assert reservation["status"] == "ACTIVE"
            assert reservation["consumed_quantity"] is None

            cur.execute(
                "SELECT physical_quantity, reserved_quantity FROM vendor_inventory WHERE vendor_product_id = %s",
                (data["vendor_product_id"],),
            )
            inv = cur.fetchone()
            assert inv["physical_quantity"] == 100
            assert inv["reserved_quantity"] == 10


def test_vendor_partial_proposal_validates_reason_and_reduction(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            with pytest.raises(ValueError):
                _propose(cur, data, accepted_quantity=7, reason="")
            with pytest.raises(ValueError):
                _propose(cur, data, accepted_quantity=10, reason=None)


def test_vendor_partial_proposal_is_tenant_and_state_protected(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)

            with pytest.raises(PermissionError):
                POLApplicationBoundary(
                    cur,
                    ApplicationContext(
                        user_id=data["vendor_user"],
                        organization_id=data["retailer_org"],
                        correlation_id=f"cross-{uuid4()}",
                    ),
                ).vendor_partial_acceptance_propose(
                    order_id=data["order_id"],
                    idempotency_key=str(uuid4()),
                    items=[
                        {
                            "order_item_id": data["order_item_id"],
                            "accepted_quantity": 7,
                            "reason": "SHORTAGE",
                        }
                    ],
                )

            cur.execute(
                "UPDATE orders SET order_status = 'ACCEPTED' WHERE id = %s",
                (data["order_id"],),
            )
            with pytest.raises(ValueError):
                _propose(cur, data)


def test_retailer_can_decline_without_inventory_mutation(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            proposal = _propose(cur, data)

            result = _retailer_boundary(cur, data).retailer_partial_acceptance_decline(
                order_id=data["order_id"],
                proposal_id=proposal["proposal_id"],
                reason="Need full quantity",
            )
            assert result["status"] == "DECLINED"
            assert result["order_status"] == "SUBMITTED"

            cur.execute(
                "SELECT status FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            assert cur.fetchone()["status"] == "ACTIVE"

            cur.execute(
                "SELECT physical_quantity, reserved_quantity FROM vendor_inventory WHERE vendor_product_id = %s",
                (data["vendor_product_id"],),
            )
            inv = cur.fetchone()
            assert inv["physical_quantity"] == 100
            assert inv["reserved_quantity"] == 10

            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM outbox_events
                WHERE event_name = 'ORDER_PARTIAL_ACCEPTANCE_DECLINED'
                  AND aggregate_id = %s
                  AND target_user_id = %s
                  AND target_organization_id = %s
                """,
                (data["order_id"], data["vendor_user"], data["vendor_org"]),
            )
            assert cur.fetchone()["count"] == 1


def test_retailer_approval_reconciles_order_inventory_amounts_and_outbox(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            proposal = _propose(cur, data, accepted_quantity=7)

            result = _retailer_boundary(cur, data).retailer_partial_acceptance_approve(
                order_id=data["order_id"],
                proposal_id=proposal["proposal_id"],
            )
            assert result["order_status"] == "PARTIALLY_ACCEPTED"
            assert result["total_amount_toman"] == 3500000
            assert result["changed_item_count"] == 1
            assert result["consumed_reservation_count"] == 1

            cur.execute(
                "SELECT order_status, total_amount_toman FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            order = cur.fetchone()
            assert order["order_status"] == "PARTIALLY_ACCEPTED"
            assert order["total_amount_toman"] == 3500000

            cur.execute(
                "SELECT accepted_quantity, total_line_amount_toman, fulfillment_status FROM order_items WHERE id = %s",
                (data["order_item_id"],),
            )
            item = cur.fetchone()
            assert item["accepted_quantity"] == 7
            assert item["total_line_amount_toman"] == 3500000
            assert item["fulfillment_status"] == "SHORTAGE"

            cur.execute(
                "SELECT status, consumed_quantity FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            reservation = cur.fetchone()
            assert reservation["status"] == "CONSUMED"
            assert reservation["consumed_quantity"] == 7

            cur.execute(
                "SELECT physical_quantity, reserved_quantity FROM vendor_inventory WHERE vendor_product_id = %s",
                (data["vendor_product_id"],),
            )
            inv = cur.fetchone()
            assert inv["physical_quantity"] == 93
            assert inv["reserved_quantity"] == 0

            cur.execute(
                "SELECT total_amount_toman FROM order_groups WHERE id = %s",
                (data["order_group_id"],),
            )
            assert cur.fetchone()["total_amount_toman"] == 3500000

            cur.execute(
                "SELECT status FROM order_partial_acceptance_proposals WHERE id = %s",
                (proposal["proposal_id"],),
            )
            assert cur.fetchone()["status"] == "ACCEPTED"

            cur.execute(
                "SELECT COUNT(*) AS count FROM outbox_events WHERE event_name = 'ORDER_PARTIALLY_ACCEPTED' AND aggregate_id = %s",
                (data["order_id"],),
            )
            assert cur.fetchone()["count"] == 2


def test_retailer_approval_is_tenant_protected(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            proposal = _propose(cur, data)

            with pytest.raises(PermissionError):
                POLApplicationBoundary(
                    cur,
                    ApplicationContext(
                        user_id=data["vendor_user"],
                        organization_id=data["vendor_org"],
                        correlation_id=f"wrong-{uuid4()}",
                    ),
                ).retailer_partial_acceptance_approve(
                    order_id=data["order_id"],
                    proposal_id=proposal["proposal_id"],
                )

            cur.execute(
                "SELECT order_status FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "SUBMITTED"

            cur.execute(
                "SELECT status FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            assert cur.fetchone()["status"] == "ACTIVE"


def test_idempotent_partial_proposal_replay_and_payload_guard(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            idem = str(uuid4())
            boundary = _vendor_boundary(cur, data)

            first = boundary.vendor_partial_acceptance_propose(
                order_id=data["order_id"],
                idempotency_key=idem,
                items=[
                    {
                        "order_item_id": data["order_item_id"],
                        "accepted_quantity": 7,
                        "reason": "SHORTAGE",
                    }
                ],
            )
            replay = boundary.vendor_partial_acceptance_propose(
                order_id=data["order_id"],
                idempotency_key=idem,
                items=[
                    {
                        "order_item_id": data["order_item_id"],
                        "accepted_quantity": 7,
                        "reason": "SHORTAGE",
                    }
                ],
            )
            assert replay["proposal_id"] == first["proposal_id"]
            assert replay["idempotent_replay"] is True

            with pytest.raises(ValueError):
                boundary.vendor_partial_acceptance_propose(
                    order_id=data["order_id"],
                    idempotency_key=idem,
                    items=[
                        {
                            "order_item_id": data["order_item_id"],
                            "accepted_quantity": 6,
                            "reason": "SHORTAGE",
                        }
                    ],
                )


def test_full_vendor_accept_is_blocked_while_partial_proposal_is_pending(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _propose(cur, data)

            with pytest.raises(ValueError):
                _vendor_boundary(cur, data).vendor_order_accept(
                    order_id=data["order_id"]
                )

            cur.execute(
                "SELECT order_status FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "SUBMITTED"
