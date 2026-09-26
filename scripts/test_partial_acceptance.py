"""PostgreSQL integration tests for the two-party partial acceptance contract."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary


@pytest.fixture
def pg_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=int(
            os.environ.get("POL_API_DB_PORT")
            or os.environ.get("POL_PG_PORT")
            or os.environ.get("PGPORT", "5432")
        ),
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
        password=os.environ.get("POL_API_DB_PASSWORD") or os.environ.get("PGPASSWORD"),
    )
    try:
        yield conn
    finally:
        conn.close()


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
            cur.execute(
                "SELECT event_name FROM outbox_events WHERE aggregate_type='INVENTORY_RESERVATION' AND aggregate_id=%s ORDER BY event_name",
                (data["reservation_id"],),
            )
            reservation_events = {row["event_name"] for row in cur.fetchall()}
            assert "INVENTORY_RESERVATION_CONSUMED" in reservation_events
            assert "INVENTORY_RESERVATION_RELEASED" in reservation_events

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
                "SELECT order_group_id FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            order_group_id = cur.fetchone()["order_group_id"]
            cur.execute(
                "SELECT total_amount_toman FROM order_groups WHERE id = %s",
                (order_group_id,),
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


def test_retailer_staff_cannot_decide_partial_acceptance(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            proposal = _propose(cur, data)

            staff_user_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO users (id, phone_number, full_name, role, is_active)
                VALUES (%s, %s, 'Partial Decision Staff', 'RETAILER_STAFF', TRUE)
                """,
                (staff_user_id, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                """
                INSERT INTO organization_memberships
                    (id, organization_id, user_id, role, status, is_primary)
                VALUES (%s, %s, %s, 'RETAILER_STAFF', 'ACTIVE', FALSE)
                """,
                (str(uuid4()), data["retailer_org"], staff_user_id),
            )

            try:
                with pytest.raises(PermissionError):
                    POLApplicationBoundary(
                        cur,
                        ApplicationContext(
                            user_id=staff_user_id,
                            organization_id=data["retailer_org"],
                            correlation_id=f"staff-decision-{uuid4()}",
                        ),
                    ).retailer_partial_acceptance_approve(
                        order_id=data["order_id"],
                        proposal_id=proposal["proposal_id"],
                    )

                cur.execute(
                    "SELECT status FROM order_partial_acceptance_proposals WHERE id=%s",
                    (proposal["proposal_id"],),
                )
                assert cur.fetchone()["status"] == "PENDING"
            finally:
                cur.execute("DELETE FROM users WHERE id=%s", (staff_user_id,))


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



def test_partial_acceptance_proposals_list_is_tenant_scoped(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            proposal = _propose(cur, data, accepted_quantity=7)

            vendor_result = _vendor_boundary(cur, data).partial_acceptance_proposals_list(
                order_id=data["order_id"]
            )
            assert len(vendor_result["proposals"]) == 1
            row = vendor_result["proposals"][0]
            assert row["proposal_id"] == proposal["proposal_id"]
            assert row["status"] == "PENDING"
            assert row["items"][0]["accepted_quantity"] == 7

            with pytest.raises(PermissionError):
                POLApplicationBoundary(
                    cur,
                    ApplicationContext(
                        user_id=data["retailer_user"],
                        organization_id=data["vendor_org"],
                        correlation_id=f"cross-list-{uuid4()}",
                    ),
                ).partial_acceptance_proposals_list(
                    order_id=data["order_id"]
                )
