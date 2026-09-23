#!/usr/bin/env python3
"""Canonical regression test for daily inventory reminder responsibility routing."""

import uuid

from psycopg2.extras import RealDictCursor

from scripts.domain_services import DailyInventoryService
from scripts.migration_runner import get_connection


def test_daily_inventory_reminder_requires_and_uses_primary_responsibility():
    conn, _ = get_connection("pol_test")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        vendor_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        org_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Canonical Reminder Vendor','VENDOR','ACTIVE')",
            (org_id,),
        )
        cur.execute(
            "INSERT INTO users (id,phone_number,full_name,role) VALUES (%s,%s,'Warehouse Manager','VENDOR_OWNER')",
            (user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"),
        )
        cur.execute(
            """
            INSERT INTO vendors (id,user_id,organization_id,business_name,warehouse_address,min_order_value_toman)
            VALUES (%s,%s,%s,'Canonical Vendor','Ahvaz Warehouse',5000000)
            """,
            (vendor_id, user_id, org_id),
        )
        cur.execute(
            """
            UPDATE vendor_inventory_responsibilities
            SET is_primary = TRUE, effective_until = NULL
            WHERE vendor_id = %s AND user_id = %s AND responsibility_type = 'WAREHOUSE_INVENTORY'
            """,
            (vendor_id, user_id),
        )
        conn.commit()

        reminders = DailyInventoryService.process_daily_reminders(cur, "2026-10-01")
        conn.commit()
        matching = [r for r in reminders if str(r["aggregate_id"]) == vendor_id]
        assert len(matching) == 1

        cur.execute(
            """
            SELECT target_user_id,target_organization_id,channel_hint
            FROM outbox_events
            WHERE event_name='DAILY_INVENTORY_REMINDER' AND aggregate_id=%s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (vendor_id,),
        )
        event = cur.fetchone()
        assert str(event["target_user_id"]) == user_id
        assert str(event["target_organization_id"]) == org_id
        assert event["channel_hint"] == "PUSH"

        reminders_again = DailyInventoryService.process_daily_reminders(cur, "2026-10-01")
        conn.commit()
        assert not [r for r in reminders_again if str(r["aggregate_id"]) == vendor_id]
    finally:
        conn.rollback()
        conn.close()
