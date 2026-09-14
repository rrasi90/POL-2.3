#!/usr/bin/env python3
"""Cross-domain worker tests for notification routing and delivery recursion."""

import uuid
from datetime import date
from psycopg2.extras import RealDictCursor

from scripts.migration_runner import get_connection
from scripts.canonical_integration_worker import CanonicalIntegrationWorker, IntegrationWorkerError


def _conn():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    return conn


def test_notification_creates_delivery_record_without_recursive_outbox():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org = str(uuid.uuid4())
        user = str(uuid.uuid4())
        notif = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'OPERATOR','ACTIVE')",
            (org, "Delivery Worker Org"),
        )
        cur.execute(
            "INSERT INTO users (id,phone_number,full_name,role) VALUES (%s,%s,%s,'OPS_AGENT')",
            (user, f"+98990{uuid.uuid4().int % 100000000:08d}", "Delivery Worker"),
        )
        cur.execute(
            """
            INSERT INTO notifications (id,user_id,organization_id,event_name,title,body,priority)
            VALUES (%s,%s,%s,'FEEDBACK_REPLIED','t','b','NORMAL')
            """,
            (notif, user, org),
        )
        cur.execute(
            "SELECT channel,status FROM notification_deliveries WHERE notification_id=%s",
            (notif,),
        )
        assert cur.fetchone()["channel"] == "INBOX"
        cur.execute(
            "SELECT COUNT(*) AS c FROM outbox_events WHERE event_name='NOTIFICATION_DELIVERY_REQUESTED' AND aggregate_id=%s",
            (notif,),
        )
        assert cur.fetchone()["c"] == 0
    finally:
        conn.rollback()
        conn.close()


def test_daily_inventory_requires_canonical_warehouse_responsibility():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org = str(uuid.uuid4())
        owner = str(uuid.uuid4())
        vendor = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
            (org, "Responsibility Vendor"),
        )
        cur.execute(
            "INSERT INTO users (id,phone_number,full_name,role) VALUES (%s,%s,%s,'VENDOR_OWNER')",
            (owner, f"+98991{uuid.uuid4().int % 100000000:08d}", "Warehouse Owner"),
        )
        cur.execute(
            "INSERT INTO organization_memberships (organization_id,user_id,role,status) VALUES (%s,%s,'VENDOR_OWNER','ACTIVE')",
            (org, owner),
        )
        cur.execute(
            """
            INSERT INTO vendors (id,user_id,organization_id,business_name,warehouse_address,min_order_value_toman)
            VALUES (%s,%s,%s,'Responsibility Vendor','Ahvaz',0)
            """,
            (vendor, owner, org),
        )
        event_id = f"canonical_inv_{uuid.uuid4().hex}"
        cur.execute(
            """
            INSERT INTO outbox_events (id,event_id,event_name,aggregate_type,aggregate_id,payload,status)
            VALUES (%s,%s,'DAILY_INVENTORY_REMINDER','VENDOR_INVENTORY',%s,'{}'::jsonb,'PENDING')
            """,
            (str(uuid.uuid4()), event_id, vendor),
        )
        row = cur.fetchone() if False else None
        conn.rollback()

        conn = _conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT COUNT(*) AS c FROM vendor_inventory_responsibilities WHERE vendor_id=%s", (vendor,))
        assert cur.fetchone()["c"] == 0
        try:
            cur.execute(
                """
                INSERT INTO outbox_events (id,event_id,event_name,aggregate_type,aggregate_id,payload,status)
                VALUES (%s,%s,'DAILY_INVENTORY_REMINDER','VENDOR_INVENTORY',%s,'{}'::jsonb,'PENDING')
                """,
                (str(uuid.uuid4()), f"missing_resp_{uuid.uuid4().hex}", vendor),
            )
            raise AssertionError("Expected reminder routing to require canonical responsibility")
        except Exception as exc:
            assert "warehouse-inventory responsibility" in str(exc)
    finally:
        conn.rollback()
        conn.close()


def test_integration_worker_uses_exact_recipient_and_template():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org = str(uuid.uuid4())
        user = str(uuid.uuid4())
        event_id = f"ORDER_ACCEPTED_{uuid.uuid4().hex}"
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'VENDOR','ACTIVE')",
            (org, "Template Vendor"),
        )
        cur.execute(
            "INSERT INTO users (id,phone_number,full_name,role) VALUES (%s,%s,%s,'VENDOR_OWNER')",
            (user, f"+98992{uuid.uuid4().int % 100000000:08d}", "Template User"),
        )
        cur.execute(
            """
            INSERT INTO outbox_events (
                id,event_id,event_name,aggregate_type,aggregate_id,payload,status,
                target_user_id,target_organization_id,channel_hint,dedupe_key
            ) VALUES (%s,%s,'ORDER_ACCEPTED','ORDER',%s,%s,'PENDING',%s,%s,'INBOX',%s)
            """,
            (
                str(uuid.uuid4()), event_id, str(uuid.uuid4()), '{"order_number":"POL-TEST"}',
                user, org, event_id,
            ),
        )
        processed = CanonicalIntegrationWorker.process_pending(cur, limit=10)
        assert processed == 1
        cur.execute(
            "SELECT user_id,organization_id,event_name,title,body FROM notifications WHERE event_name='ORDER_ACCEPTED' ORDER BY created_at DESC LIMIT 1"
        )
        notification = cur.fetchone()
        assert str(notification["user_id"]) == user
        assert str(notification["organization_id"]) == org
        assert notification["title"] == "سفارش پذیرفته شد"
        cur.execute(
            "SELECT status FROM outbox_events WHERE event_id=%s",
            (event_id,),
        )
        assert cur.fetchone()["status"] == "PUBLISHED"
    finally:
        conn.rollback()
        conn.close()
