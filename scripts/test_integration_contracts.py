#!/usr/bin/env python3
"""Cross-domain integration contract tests for POL."""

import ast
import uuid
from pathlib import Path

from psycopg2.extras import RealDictCursor

from scripts.migration_runner import get_connection
from scripts.operational_policies import (
    AllocationIntegrityError,
    NotificationRoutingPolicy,
    validate_vendor_operational_capacity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _conn():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    return conn


def test_notification_insert_seeds_delivery_without_recursive_outbox():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        notification_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, %s, 'OPERATOR', 'ACTIVE')",
            (org_id, "Integration Operator"),
        )
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, %s, 'OPS_AGENT')",
            (user_id, f"+98910{uuid.uuid4().int % 100000000:08d}", "Integration Test User"),
        )
        cur.execute(
            """
            INSERT INTO notifications (
                id, user_id, organization_id, event_name, title, body, priority
            ) VALUES (%s, %s, %s, 'FEEDBACK_REPLIED', 'Test', 'Test body', 'NORMAL')
            """,
            (notification_id, user_id, org_id),
        )
        cur.execute(
            "SELECT channel,status FROM notification_deliveries WHERE notification_id=%s",
            (notification_id,),
        )
        row = cur.fetchone()
        assert row is not None
        assert row["channel"] == "INBOX"
        assert row["status"] == "PENDING"
        cur.execute(
            "SELECT COUNT(*) AS c FROM outbox_events WHERE event_name='NOTIFICATION_DELIVERY_REQUESTED' AND aggregate_id=%s",
            (notification_id,),
        )
        assert cur.fetchone()["c"] == 0
    finally:
        conn.rollback()
        conn.close()


def test_daily_inventory_reminder_has_explicit_vendor_recipient():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        vendor_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, %s, 'VENDOR', 'ACTIVE')",
            (org_id, "Reminder Vendor Org"),
        )
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, %s, 'VENDOR_OWNER')",
            (user_id, f"+98911{uuid.uuid4().int % 100000000:08d}", "Warehouse Responsible"),
        )
        cur.execute(
            """
            INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
            VALUES (%s, %s, %s, 'Reminder Vendor', 'Ahvaz', 0)
            """,
            (vendor_id, user_id, org_id),
        )
        event_id = f"integration_daily_reminder_{uuid.uuid4().hex}"
        cur.execute(
            """
            INSERT INTO outbox_events (
                id, event_id, event_name, aggregate_type, aggregate_id, payload, status
            ) VALUES (
                %s, %s, 'DAILY_INVENTORY_REMINDER', 'VENDOR_INVENTORY', %s,
                %s, 'PENDING'
            )
            """,
            (
                str(uuid.uuid4()), event_id, vendor_id,
                '{"confirmation_date":"2026-10-01"}',
            ),
        )
        cur.execute(
            "SELECT target_user_id, target_organization_id, channel_hint, dedupe_key FROM outbox_events WHERE event_id=%s",
            (event_id,),
        )
        row = cur.fetchone()
        assert str(row["target_user_id"]) == user_id
        assert str(row["target_organization_id"]) == org_id
        assert row["channel_hint"] == "PUSH"
        assert row["dedupe_key"] == event_id
        cur.execute(
            "SELECT status FROM daily_inventory_confirmations WHERE vendor_id=%s AND confirmation_date='2026-10-01'",
            (vendor_id,),
        )
        assert cur.fetchone()["status"] == "PENDING"
    finally:
        conn.rollback()
        conn.close()


def test_vendor_capacity_is_a_real_checkout_boundary():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        vendor_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organizations (id, name, org_type, status) VALUES (%s, %s, 'VENDOR', 'ACTIVE')",
            (org_id, "Capacity Vendor Org"),
        )
        cur.execute(
            "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, %s, 'VENDOR_OWNER')",
            (user_id, f"+98912{uuid.uuid4().int % 100000000:08d}", "Capacity Vendor"),
        )
        cur.execute(
            """
            INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
            VALUES (%s, %s, %s, 'Capacity Vendor', 'Ahvaz', 0)
            """,
            (vendor_id, user_id, org_id),
        )
        cur.execute(
            """
            INSERT INTO vendor_capacity_profiles (id, vendor_id, max_orders_per_day, timezone, is_active)
            VALUES (%s, %s, 0, 'Asia/Tehran', TRUE)
            """,
            (str(uuid.uuid4()), vendor_id),
        )
        try:
            validate_vendor_operational_capacity(
                cur,
                [{"vendor_id": vendor_id, "quantity": 1, "amount_toman": 1000}],
            )
            raise AssertionError("Configured zero daily capacity must reject checkout")
        except AllocationIntegrityError as exc:
            assert "capacity exhausted" in str(exc)
    finally:
        conn.rollback()
        conn.close()


def test_notification_recipient_policy_rejects_implicit_routing():
    try:
        NotificationRoutingPolicy.require_explicit_recipient(None, "org")
        raise AssertionError("Missing target user must be rejected")
    except ValueError:
        pass


def test_domain_services_do_not_create_external_delivery_side_effects():
    source = (SCRIPTS_DIR / "domain_services.py").read_text(encoding="utf-8")
    forbidden_markers = [
        "requests.post(",
        "httpx.post(",
        "boto3.client(",
        "send_sms(",
        "send_push(",
    ]
    offenders = [marker for marker in forbidden_markers if marker in source]
    assert offenders == [], f"External provider calls leaked into domain_services.py: {offenders}"


def test_route_contract_document_and_canonical_gateway_exist():
    assert (REPO_ROOT / "POL_00_PROJECT_CONTROL" / "INTEGRATION_CONTRACTS.md").exists()
    source = (SCRIPTS_DIR / "checkout_gateway.py").read_text(encoding="utf-8")
    assert "validate_allocation_against_basket" in source
    assert "RevalidationCheckoutService" in source

    tree = ast.parse(source)
    classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    assert "CanonicalCheckoutGateway" in classes
