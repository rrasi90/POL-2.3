#!/usr/bin/env python3
"""Cross-domain worker tests for notification routing and delivery recursion."""

import uuid

import pytest
from psycopg2.extras import RealDictCursor

from scripts.test_e2e_mvp_platform import postgres_database, insert_row, transaction

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
        delivery = cur.fetchone()
        assert delivery["channel"] == "INBOX"
        assert delivery["status"] == "PENDING"
        cur.execute(
            "SELECT COUNT(*) AS c FROM outbox_events WHERE event_name='NOTIFICATION_DELIVERY_REQUESTED' AND aggregate_id=%s",
            (notif,),
        )
        assert cur.fetchone()["c"] == 0
    finally:
        conn.rollback()
        conn.close()


def test_daily_inventory_materializes_canonical_warehouse_responsibility():
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
        cur.execute(
            """
            SELECT r.user_id, r.is_primary, r.responsibility_type
            FROM vendor_inventory_responsibilities r
            WHERE r.vendor_id=%s
            """,
            (vendor,),
        )
        responsibility = cur.fetchone()
        assert str(responsibility["user_id"]) == owner
        assert responsibility["is_primary"] is True
        assert responsibility["responsibility_type"] == "WAREHOUSE_INVENTORY"

        cur.execute(
            "SELECT target_user_id,target_organization_id,channel_hint FROM outbox_events WHERE event_id=%s",
            (event_id,),
        )
        routed = cur.fetchone()
        assert str(routed["target_user_id"]) == owner
        assert str(routed["target_organization_id"]) == org
        assert routed["channel_hint"] == "PUSH"
    finally:
        conn.rollback()
        conn.close()


def test_integration_worker_uses_exact_recipient_and_template(postgres_database):
    # Use a fresh PostgreSQL 18 database for this worker test. Shared pol_test state can
    # contain unrelated PENDING outbox events from other tests, making process_pending()
    # legitimately process more than this test's event.
    with transaction(postgres_database) as cur:
        org = str(uuid.uuid4())
        user = str(uuid.uuid4())
        event_id = f"ORDER_ACCEPTED_{uuid.uuid4().hex}"
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,%s,'RETAILER','ACTIVE')",
            (org, "Template Retailer"),
        )
        cur.execute(
            "INSERT INTO users (id,phone_number,full_name,role) VALUES (%s,%s,%s,'RETAILER_OWNER')",
            (user, f"+98992{uuid.uuid4().int % 100000000:08d}", "Template User"),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships (organization_id,user_id,role,status)
            VALUES (%s,%s,'RETAILER_OWNER','ACTIVE')
            """,
            (org, user),
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


@pytest.mark.parametrize("routing", [
    "authorized", "wrong_organization", "suspended", "revoked", "inactive_organization", "missing_user", "missing_organization",
])
def test_batch4_recipient_membership_isolation(postgres_database, routing):
    with transaction(postgres_database) as cur:
        org = insert_row(cur, "organizations", name="Recipient tenant", org_type="RETAILER", status="ACTIVE")
        other = insert_row(cur, "organizations", name="Other tenant", org_type="RETAILER", status="ACTIVE")
        user = insert_row(
            cur, "users", phone_number="+989161234567", full_name="Recipient", role="RETAILER_OWNER",
        )
        insert_row(
            cur, "organization_memberships", user_id=user["id"], organization_id=org["id"],
            role="RETAILER_OWNER", status="ACTIVE",
        )
        target_org = other["id"] if routing == "wrong_organization" else org["id"]
        event_id = "batch4-" + uuid.uuid4().hex
        insert_row(
            cur, "outbox_events", event_id=event_id, event_name="ORDER_ACCEPTED",
            aggregate_type="ORDER", aggregate_id=str(uuid.uuid4()), payload='{}',
            target_user_id=None if routing == "missing_user" else user["id"],
            target_organization_id=None if routing == "missing_organization" else target_org,
            dedupe_key=event_id, channel_hint="INBOX",
        )
        if routing in {"suspended", "revoked"}:
            cur.execute("UPDATE organization_memberships SET status=%s WHERE user_id=%s", (routing.upper(), user["id"]))
        if routing == "inactive_organization":
            cur.execute("UPDATE organizations SET status='SUSPENDED' WHERE id=%s", (org["id"],))
    with transaction(postgres_database) as cur:
        if routing == "authorized":
            assert CanonicalIntegrationWorker.process_pending(cur) == 1
            assert CanonicalIntegrationWorker.process_pending(cur) == 0
        else:
            assert CanonicalIntegrationWorker.process_pending(cur) == 1
        cur.execute(
            """
            SELECT user_id, organization_id
            FROM notifications
            WHERE user_id=%s AND organization_id=%s AND event_name='ORDER_ACCEPTED'
            ORDER BY created_at DESC
            """,
            (user["id"], org["id"]),
        )
        rows = cur.fetchall()
        assert len(rows) == (1 if routing == "authorized" else 0)
        if rows:
            assert rows[0]["user_id"] == user["id"]
            assert rows[0]["organization_id"] == org["id"]
        cur.execute(
            """
            SELECT COUNT(*) AS count
            FROM notification_deliveries nd
            JOIN notifications n ON n.id=nd.notification_id
            WHERE n.user_id=%s AND n.organization_id=%s AND n.event_name='ORDER_ACCEPTED'
            """,
            (user["id"], org["id"]),
        )
        assert cur.fetchone()["count"] == len(rows)
        cur.execute("SELECT status, last_error FROM outbox_events WHERE event_id=%s", (event_id,))
        event_row = cur.fetchone()
        assert event_row["status"] == ("PUBLISHED" if routing == "authorized" else "FAILED")
        if routing != "authorized":
            assert event_row["last_error"]
    with transaction(postgres_database) as cur:
        cur.execute(
            """
            SELECT COUNT(*) AS count
            FROM notifications
            WHERE user_id=%s AND organization_id=%s AND event_name='ORDER_ACCEPTED'
            """,
            (user["id"], org["id"]),
        )
        assert cur.fetchone()["count"] == (1 if routing == "authorized" else 0)
