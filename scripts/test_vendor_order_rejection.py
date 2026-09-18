"""PostgreSQL integration tests for canonical vendor order rejection."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.test_vendor_order_acceptance import _setup_order


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


def _boundary(cur, data):
    return POLApplicationBoundary(
        cur,
        ApplicationContext(
            user_id=data["vendor_user"],
            organization_id=data["vendor_org"],
            correlation_id=f"reject-{uuid4()}",
        ),
    )


def test_vendor_reject_releases_reservation_and_notifies_retailer(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            result = _boundary(cur, data).vendor_order_reject(
                order_id=data["order_id"],
                rejection_reason="Out of physical stock",
            )

            assert result["order_status"] == "REJECTED"
            assert result["rejection_reason"] == "Out of physical stock"
            assert result["released_reservation_count"] == 1

            cur.execute(
                "SELECT order_status, rejection_reason FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            order = cur.fetchone()
            assert order["order_status"] == "REJECTED"
            assert order["rejection_reason"] == "Out of physical stock"

            cur.execute(
                "SELECT status, released_at FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            reservation = cur.fetchone()
            assert reservation["status"] == "RELEASED"
            assert reservation["released_at"] is not None

            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                """,
                (data["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            assert inventory["physical_quantity"] == 100
            assert inventory["reserved_quantity"] == 0

            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM outbox_events
                WHERE event_name = 'ORDER_REJECTED'
                  AND aggregate_id = %s
                  AND target_user_id = %s
                  AND target_organization_id = %s
                  AND status = 'PENDING'
                """,
                (data["order_id"], data["retailer_user"], data["retailer_org"]),
            )
            assert cur.fetchone()["count"] == 1


def test_vendor_reject_is_tenant_protected(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            rogue_user = str(uuid4())
            rogue_org = str(uuid4())

            cur.execute(
                """
                INSERT INTO users (id, phone_number, full_name, role)
                VALUES (%s, %s, 'Rogue Vendor', 'VENDOR_OWNER')
                """,
                (rogue_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                """
                INSERT INTO organizations (id, name, org_type, status)
                VALUES (%s, 'Rogue Vendor Org', 'VENDOR', 'ACTIVE')
                """,
                (rogue_org,),
            )
            cur.execute(
                """
                INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
                VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')
                """,
                (str(uuid4()), rogue_org, rogue_user),
            )

            with pytest.raises(PermissionError):
                POLApplicationBoundary(
                    cur,
                    ApplicationContext(
                        user_id=rogue_user,
                        organization_id=rogue_org,
                        correlation_id=f"rogue-{uuid4()}",
                    ),
                ).vendor_order_reject(
                    order_id=data["order_id"],
                    rejection_reason="Rogue mutation",
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

            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                """,
                (data["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            assert inventory["physical_quantity"] == 100
            assert inventory["reserved_quantity"] == 10


def test_vendor_reject_invalid_state_is_atomic(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            cur.execute(
                "UPDATE orders SET order_status = 'ACCEPTED' WHERE id = %s",
                (data["order_id"],),
            )

            with pytest.raises(ValueError):
                _boundary(cur, data).vendor_order_reject(
                    order_id=data["order_id"],
                    rejection_reason="Already accepted",
                )

            cur.execute(
                "SELECT order_status FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "ACCEPTED"

            cur.execute(
                "SELECT status FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            assert cur.fetchone()["status"] == "ACTIVE"

            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                """,
                (data["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            assert inventory["physical_quantity"] == 100
            assert inventory["reserved_quantity"] == 10


def test_vendor_reject_requires_non_empty_reason(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            with pytest.raises(ValueError):
                _boundary(cur, data).vendor_order_reject(
                    order_id=data["order_id"],
                    rejection_reason="   ",
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
