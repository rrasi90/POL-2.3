"""Integration tests for canonical vendor-acceptance timeout automation."""

from __future__ import annotations

from datetime import date, datetime
import os
from uuid import uuid4
import zoneinfo

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.sla_calendar import calculate_sla_deadline
from scripts.test_vendor_order_acceptance import _setup_order


TEHRAN_TZ = zoneinfo.ZoneInfo("Asia/Tehran")

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

def _ops_user(cur):
    user_id = str(uuid4())
    org_id = str(uuid4())
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Timeout Ops', 'OPS_ADMIN')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Timeout Ops Org', 'OPERATOR', 'ACTIVE')",
        (org_id,),
    )
    cur.execute(
        """
        INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
        VALUES (%s, %s, %s, 'OPS_ADMIN', 'ACTIVE')
        """,
        (str(uuid4()), org_id, user_id),
    )
    return user_id, org_id


def _field_activator(cur):
    user_id = str(uuid4())
    org_id = str(uuid4())
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Timeout Field Activator', 'FIELD_ACTIVATOR')",
        (user_id, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Timeout Field Org', 'OPERATOR', 'ACTIVE')",
        (org_id,),
    )
    cur.execute(
        """
        INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
        VALUES (%s, %s, %s, 'FIELD_ACTIVATOR', 'ACTIVE')
        """,
        (str(uuid4()), org_id, user_id),
    )
    return user_id


def _ops_boundary(cur):
    user_id, org_id = _ops_user(cur)
    _field_activator(cur)
    return user_id, POLApplicationBoundary(
        cur,
        ApplicationContext(
            user_id=user_id,
            organization_id=org_id,
            correlation_id=f"timeout-{uuid4()}",
        ),
    )


def test_production_sla_calendar_matches_ahvaz_rules():
    thursday = datetime(2026, 9, 17, 17, 0, tzinfo=TEHRAN_TZ)
    assert calculate_sla_deadline(thursday, 2.0) == datetime(
        2026, 9, 19, 9, 0, tzinfo=TEHRAN_TZ
    )

    holiday_start = datetime(2026, 9, 15, 17, 30, tzinfo=TEHRAN_TZ)
    assert calculate_sla_deadline(
        holiday_start, 2.0, holidays={date(2026, 9, 16)}
    ) == datetime(2026, 9, 17, 9, 30, tzinfo=TEHRAN_TZ)


def test_timeout_cancels_releases_notifies_penalizes_and_tasks(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _, boundary = _ops_boundary(cur)

            deadline = datetime(2026, 9, 14, 12, 0, tzinfo=TEHRAN_TZ)
            cur.execute(
                "UPDATE orders SET vendor_acceptance_deadline_at = %s WHERE id = %s",
                (deadline, data["order_id"]),
            )

            result = boundary.process_vendor_acceptance_timeouts()
            assert result["cancelled_order_count"] == 1
            assert result["released_reservation_count"] == 1
            assert result["notification_event_count"] == 1
            assert result["reliability_event_count"] == 1
            assert result["operational_task_count"] == 2

            cur.execute(
                "SELECT order_status, cancellation_reason FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            order = cur.fetchone()
            assert order["order_status"] == "CANCELLED"
            assert order["cancellation_reason"] == "VENDOR_TIMEOUT"

            cur.execute(
                "SELECT status, consumed_quantity FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            reservation = cur.fetchone()
            assert reservation["status"] == "RELEASED"
            assert reservation["consumed_quantity"] == 0

            cur.execute(
                "SELECT physical_quantity, reserved_quantity FROM vendor_inventory WHERE vendor_product_id = %s",
                (data["vendor_product_id"],),
            )
            inv = cur.fetchone()
            assert inv["physical_quantity"] == 100
            assert inv["reserved_quantity"] == 0

            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM outbox_events
                WHERE event_name = 'ORDER_CANCELLED'
                  AND aggregate_id = %s
                  AND target_user_id = %s
                  AND target_organization_id = %s
                """,
                (data["order_id"], data["retailer_user"], data["retailer_org"]),
            )
            assert cur.fetchone()["count"] == 1

            cur.execute(
                "SELECT event_type, impact_score FROM vendor_reliability_events WHERE order_id = %s",
                (data["order_id"],),
            )
            reliability = cur.fetchone()
            assert reliability["event_type"] == "ACCEPTANCE_LATE"
            assert float(reliability["impact_score"]) == -0.25


def test_timeout_is_idempotent_after_status_transition(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _, boundary = _ops_boundary(cur)
            cur.execute(
                "UPDATE orders SET vendor_acceptance_deadline_at = now() - interval '1 minute' WHERE id = %s",
                (data["order_id"],),
            )

            first = boundary.process_vendor_acceptance_timeouts()
            second = boundary.process_vendor_acceptance_timeouts()

            assert first["cancelled_order_count"] == 1
            assert second["cancelled_order_count"] == 0


def test_timeout_does_not_cancel_before_deadline(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _, boundary = _ops_boundary(cur)
            cur.execute(
                "UPDATE orders SET vendor_acceptance_deadline_at = now() + interval '1 hour' WHERE id = %s",
                (data["order_id"],),
            )

            result = boundary.process_vendor_acceptance_timeouts()
            assert result["cancelled_order_count"] == 0

            cur.execute(
                "SELECT order_status FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "SUBMITTED"


def test_timeout_requires_ops_context(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            with pytest.raises(PermissionError):
                POLApplicationBoundary(
                    cur,
                    ApplicationContext(
                        user_id=data["vendor_user"],
                        organization_id=data["vendor_org"],
                        correlation_id=f"timeout-auth-{suffix}",
                    ),
                ).process_vendor_acceptance_timeouts()



def test_timeout_backfills_missing_deadline_from_created_at(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _, boundary = _ops_boundary(cur)

            created_at = datetime(2026, 9, 17, 17, 0, tzinfo=TEHRAN_TZ)
            effective_now = datetime(2026, 9, 19, 9, 1, tzinfo=TEHRAN_TZ)
            cur.execute(
                """
                UPDATE orders
                SET created_at = %s,
                    vendor_acceptance_deadline_at = NULL
                WHERE id = %s
                """,
                (created_at, data["order_id"]),
            )

            from scripts.vendor_acceptance_timeout_worker import VendorAcceptanceTimeoutWorker

            result = VendorAcceptanceTimeoutWorker.process_expired(
                cur,
                now=effective_now,
            )
            assert result["cancelled_order_count"] == 1

            cur.execute(
                "SELECT vendor_acceptance_deadline_at FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            deadline = cur.fetchone()["vendor_acceptance_deadline_at"]
            expected = datetime(2026, 9, 19, 9, 0, tzinfo=TEHRAN_TZ)
            assert deadline.astimezone(TEHRAN_TZ) == expected


def test_timeout_notification_is_tenant_scoped(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _, boundary = _ops_boundary(cur)

            other_user = str(uuid4())
            other_org = str(uuid4())
            cur.execute(
                """
                INSERT INTO users (id, phone_number, full_name, role)
                VALUES (%s, %s, 'Unrelated Retailer', 'RETAILER_OWNER')
                """,
                (other_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                """
                INSERT INTO organizations (id, name, org_type, status)
                VALUES (%s, 'Unrelated Retailer Org', 'RETAILER', 'ACTIVE')
                """,
                (other_org,),
            )
            cur.execute(
                """
                INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
                VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')
                """,
                (str(uuid4()), other_org, other_user),
            )

            cur.execute(
                "UPDATE orders SET vendor_acceptance_deadline_at = now() - interval '1 minute' WHERE id = %s",
                (data["order_id"],),
            )
            boundary.process_vendor_acceptance_timeouts()

            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM outbox_events
                WHERE event_name = 'ORDER_CANCELLED'
                  AND aggregate_id = %s
                  AND target_user_id = %s
                """,
                (data["order_id"], other_user),
            )
            assert cur.fetchone()["count"] == 0

            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM outbox_events
                WHERE event_name = 'ORDER_CANCELLED'
                  AND aggregate_id = %s
                  AND target_organization_id = %s
                """,
                (data["order_id"], other_org),
            )
            assert cur.fetchone()["count"] == 0


def test_timeout_assignee_selection_is_deterministic(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            ops_user, _ = _ops_user(cur)
            field_user = _field_activator(cur)

            second_ops_user, second_ops_org = _ops_user(cur)
            second_field_user = _field_activator(cur)

            cur.execute(
                "UPDATE orders SET vendor_acceptance_deadline_at = now() - interval '1 minute' WHERE id = %s",
                (data["order_id"],),
            )

            from scripts.vendor_acceptance_timeout_worker import VendorAcceptanceTimeoutWorker

            VendorAcceptanceTimeoutWorker.process_expired(cur)

            cur.execute(
                """
                SELECT user_id
                FROM organization_memberships
                WHERE role = 'FIELD_ACTIVATOR'
                  AND status = 'ACTIVE'
                ORDER BY user_id
                LIMIT 1
                """
            )
            expected_field_user = cur.fetchone()["user_id"]

            cur.execute(
                """
                SELECT user_id
                FROM organization_memberships
                WHERE role IN ('OPS_ADMIN', 'SUPER_ADMIN')
                  AND status = 'ACTIVE'
                ORDER BY user_id
                LIMIT 1
                """
            )
            expected_ops_user = cur.fetchone()["user_id"]

            cur.execute(
                """
                SELECT assigned_to_user_id
                FROM field_tasks
                WHERE task_type = 'VENDOR_TIMEOUT'
                  AND notes LIKE %s
                ORDER BY id
                """,
                (f"%{data['order_id']}%",),
            )
            assignees = [row["assigned_to_user_id"] for row in cur.fetchall()]
            assert len(assignees) == 2
            assert set(assignees) == {expected_field_user, expected_ops_user}

def test_timeout_closes_pending_partial_proposal(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            _, boundary = _ops_boundary(cur)

            from scripts.canonical_partial_acceptance import CanonicalPartialAcceptanceService

            CanonicalPartialAcceptanceService.propose(
                cur,
                user_id=data["vendor_user"],
                organization_id=data["vendor_org"],
                order_id=data["order_id"],
                idempotency_key=str(uuid4()),
                items=[{
                    "order_item_id": data["order_item_id"],
                    "accepted_quantity": 7,
                    "reason": "SHORTAGE",
                }],
            )

            cur.execute(
                "UPDATE orders SET vendor_acceptance_deadline_at = now() - interval '1 minute' WHERE id = %s",
                (data["order_id"],),
            )
            boundary.process_vendor_acceptance_timeouts()

            cur.execute(
                "SELECT status, decision_reason FROM order_partial_acceptance_proposals WHERE order_id = %s",
                (data["order_id"],),
            )
            proposal = cur.fetchone()
            assert proposal["status"] == "DECLINED"
            assert proposal["decision_reason"] == "VENDOR_TIMEOUT"
