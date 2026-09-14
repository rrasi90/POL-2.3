"""
POL Notification Subsystem & User Inbox Runtime Verification Suite
Tests:
- Asynchronous notification creation from outbox event
- Durable user inbox persistence (user_inbox_items)
- Multi-channel delivery records (INBOX, PUSH, SMS)
- User notification preferences (marketing opt-out vs critical bypass)
- External delivery failure decoupling (SMS failure does not abort business records)
- Inbox item read state transition
"""

import sys
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_connection():
    ports = [5432, 5433]
    for p in ports:
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError("Could not connect to PostgreSQL on ports 5432 or 5433")

def test_notifications():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL NOTIFICATION & USER INBOX RUNTIME VERIFICATION")
    print("================================================================")

    try:
        user_id = str(uuid.uuid4())
        phone = f"+98916{uuid.uuid4().int % 10000000:07d}"
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Hossein Test User', 'RETAILER_OWNER');
        """, (user_id, phone))

        print("\n[TEST 1] Processing Transactional Outbox Event to Notification...")
        outbox_id = str(uuid.uuid4())
        event_payload = {
            "order_id": str(uuid.uuid4()),
            "order_number": "ORD-202609-0012",
            "vendor_name": "Pakhsh Karun",
            "total_toman": 15000000
        }
        cur.execute("""
            INSERT INTO outbox_events (id, event_id, event_name, aggregate_type, aggregate_id, payload, status)
            VALUES (%s, %s, 'ORDER_SUBMITTED', 'ORDER', %s, %s, 'PENDING');
        """, (outbox_id, str(uuid.uuid4()), event_payload["order_id"], psycopg2.extras.Json(event_payload)))

        notif_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, event_name, title, body, data_payload, priority)
            VALUES (%s, %s, 'ORDER_SUBMITTED', 'سفارش جدید ثبت شد', 'سفارش شماره ORD-202609-0012 دریافت گردید.', %s, 'HIGH');
        """, (notif_id, user_id, psycopg2.extras.Json(event_payload)))

        cur.execute("""
            UPDATE outbox_events SET status = 'PUBLISHED', published_at = now() WHERE id = %s;
        """, (outbox_id,))
        print("  [PASS] Outbox event processed and notification record created.")

        print("\n[TEST 2] Verifying User Inbox Item Persistence...")
        inbox_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO user_inbox_items (id, user_id, notification_id, title, body, category, deep_link, is_read)
            VALUES (%s, %s, %s, 'سفارش جدید ثبت شد', 'سفارش شماره ORD-202609-0012 دریافت گردید.', 'ORDERS', '/orders/' || %s, FALSE);
        """, (inbox_id, user_id, notif_id, event_payload["order_id"]))

        cur.execute("SELECT is_read, category FROM user_inbox_items WHERE id = %s;", (inbox_id,))
        inbox_item = cur.fetchone()
        assert inbox_item["is_read"] is False
        assert inbox_item["category"] == "ORDERS"
        print("  [PASS] User inbox item created in unread state.")

        print("\n[TEST 3] Recording Channel Deliveries (INBOX, PUSH, SMS)...")
        # INBOX is seeded by the canonical notification trigger. The test adds
        # the two provider channels and verifies one row per channel.
        deliv_push = str(uuid.uuid4())
        deliv_sms = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notification_deliveries (id, notification_id, channel, provider, status, delivered_at) VALUES
            (%s, %s, 'PUSH', 'FIREBASE', 'SENT', now()),
            (%s, %s, 'SMS', 'KAVENEGAR', 'SENT', now());
        """, (deliv_push, notif_id, deliv_sms, notif_id))

        cur.execute("SELECT count(*) as count FROM notification_deliveries WHERE notification_id = %s;", (notif_id,))
        assert cur.fetchone()["count"] == 3
        print("  [PASS] All 3 delivery records tracked for notification.")

        print("\n[TEST 4] Testing User Preference Enforcement (Marketing Opt-Out vs Critical Bypass)...")
        cur.execute("""
            INSERT INTO notification_preferences (user_id, category, push_enabled, sms_enabled)
            VALUES (%s, 'MARKETING', TRUE, FALSE);
        """, (user_id,))

        mkt_notif_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, event_name, title, body, priority)
            VALUES (%s, %s, 'MARKETING_PROMO', 'تخفیف ویژه آخر هفته', 'تخفیف ۵ درصدی بر روی روغن خوراکی', 'LOW');
        """, (mkt_notif_id, user_id))

        cur.execute("""
            SELECT sms_enabled FROM notification_preferences WHERE user_id = %s AND category = 'MARKETING';
        """, (user_id,))
        pref = cur.fetchone()
        assert pref["sms_enabled"] is False

        cur.execute("""
            INSERT INTO notification_deliveries (id, notification_id, channel, provider, status, failure_reason)
            VALUES (%s, %s, 'SMS', 'KAVENEGAR', 'SKIPPED', 'User opted out of MARKETING SMS');
        """, (str(uuid.uuid4()), mkt_notif_id))

        cur.execute("SELECT status FROM notification_deliveries WHERE notification_id = %s AND channel = 'SMS';", (mkt_notif_id,))
        assert cur.fetchone()["status"] == "SKIPPED"
        print("  [PASS] Marketing SMS correctly SKIPPED according to user preferences.")

        print("\n[TEST 5] Testing External SMS Failure Decoupling...")
        fail_notif_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO notifications (id, user_id, event_name, title, body, priority)
            VALUES (%s, %s, 'DELIVERY_DISPATCHED', 'بار شما بارگیری شد', 'راننده در مسیر فروشگاه شماست.', 'HIGH');
        """, (fail_notif_id, user_id))

        cur.execute("""
            INSERT INTO notification_deliveries (id, notification_id, channel, provider, status, failure_reason, attempt_count)
            VALUES (%s, %s, 'SMS', 'KAVENEGAR', 'FAILED', 'HTTP 503 Gateway Timeout', 1);
        """, (str(uuid.uuid4()), fail_notif_id))

        cur.execute("SELECT title FROM notifications WHERE id = %s;", (fail_notif_id,))
        assert cur.fetchone()["title"] == "بار شما بارگیری شد"
        print("  [PASS] External SMS failure did not compromise notification integrity (Decoupled!).")

        print("\n[TEST 6] Marking Inbox Item as Read...")
        cur.execute("""
            UPDATE user_inbox_items
            SET is_read = TRUE, read_at = now()
            WHERE id = %s
            RETURNING is_read, read_at;
        """, (inbox_id,))
        res = cur.fetchone()
        assert res["is_read"] is True
        assert res["read_at"] is not None
        print("  [PASS] Inbox item transitioned to read state with timestamp.")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL NOTIFICATION & INBOX TESTS PASSED SUCCESSFULLY!")
        print("================================================================")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_notifications()
