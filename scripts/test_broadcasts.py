"""
POL Admin Broadcast Messaging & Audience Snapshot Runtime Verification Suite
Tests:
- Admin creates draft broadcast with audience targeting criteria
- Recipient snapshot freezing (broadcast_recipients)
- uq_broadcast_recipient unique constraint
- Multi-recipient dispatch to Notification engine & User Inbox
- Broadcast lifecycle: DRAFT -> SCHEDULED -> PROCESSING -> COMPLETED
- Recipient delivery state tracking
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

def test_broadcasts():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL ADMIN BROADCAST & AUDIENCE SNAPSHOT RUNTIME VERIFICATION")
    print("================================================================")

    try:
        # Setup Admin User
        admin_id = str(uuid.uuid4())
        admin_phone = f"+98916{uuid.uuid4().int % 10000000:07d}"
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Super Admin', 'SUPER_ADMIN');
        """, (admin_id, admin_phone))

        # Setup 3 Target Retailer Users & Orgs
        target_users = []
        for i in range(3):
            u_id = str(uuid.uuid4())
            o_id = str(uuid.uuid4())
            phone = f"+98916{uuid.uuid4().int % 10000000:07d}"
            cur.execute("""
                INSERT INTO organizations (id, name, org_type, status)
                VALUES (%s, 'Retailer Org ' || %s, 'RETAILER', 'ACTIVE');
            """, (o_id, i))
            cur.execute("""
                INSERT INTO users (id, phone_number, full_name, role)
                VALUES (%s, %s, 'Retailer User ' || %s, 'RETAILER_OWNER');
            """, (u_id, phone, i))
            cur.execute("""
                INSERT INTO organization_memberships (organization_id, user_id, role, status)
                VALUES (%s, %s, 'RETAILER_OWNER', 'ACTIVE');
            """, (o_id, u_id))
            target_users.append((u_id, o_id))

        # 1. Create Broadcast Message in DRAFT
        print("\n[TEST 1] Admin Creating Broadcast Message (Draft)...")
        bcast_id = str(uuid.uuid4())
        criteria = {"org_type": "RETAILER", "status": "ACTIVE", "city": "Ahvaz"}
        cur.execute("""
            INSERT INTO broadcast_messages (id, admin_user_id, title, body, target_criteria, status)
            VALUES (%s, %s, 'تعطیلی موقت انبارها در روز پنجشنبه', 'به اطلاع کلیه همکاران می‌رساند روز پنجشنبه به علت انبارگردانی کلی تحویل انجام نمی‌شود.', %s, 'DRAFT');
        """, (bcast_id, admin_id, psycopg2.extras.Json(criteria)))

        cur.execute("SELECT status FROM broadcast_messages WHERE id = %s;", (bcast_id,))
        assert cur.fetchone()["status"] == "DRAFT"
        print("  [PASS] Broadcast message created in DRAFT state.")

        # 2. Audience Resolution & Frozen Recipient Snapshot
        print("\n[TEST 2] Freezing Target Recipient Snapshot...")
        for u_id, o_id in target_users:
            cur.execute("""
                INSERT INTO broadcast_recipients (id, broadcast_id, user_id, organization_id, status)
                VALUES (%s, %s, %s, %s, 'PENDING');
            """, (str(uuid.uuid4()), bcast_id, u_id, o_id))

        cur.execute("""
            UPDATE broadcast_messages 
            SET recipient_count = (SELECT count(*) FROM broadcast_recipients WHERE broadcast_id = %s),
                status = 'SCHEDULED'
            WHERE id = %s
            RETURNING recipient_count, status;
        """, (bcast_id, bcast_id))
        res = cur.fetchone()
        assert res["recipient_count"] == 3
        assert res["status"] == "SCHEDULED"
        print(f"  [PASS] Recipient snapshot frozen: {res['recipient_count']} target recipients locked.")

        # 3. Assert uq_broadcast_recipient Unique Constraint
        print("\n[TEST 3] Testing Duplicate Recipient Snapshot Constraint...")
        conn.commit()
        dup_prevented = False
        try:
            cur.execute("""
                INSERT INTO broadcast_recipients (id, broadcast_id, user_id, organization_id, status)
                VALUES (%s, %s, %s, %s, 'PENDING');
            """, (str(uuid.uuid4()), bcast_id, target_users[0][0], target_users[0][1]))
        except psycopg2.IntegrityError:
            conn.rollback()
            dup_prevented = True
            print("  [PASS] Duplicate recipient in same broadcast prevented by uq_broadcast_recipient.")
        assert dup_prevented, "Expected duplicate recipient to be rejected!"

        # 4. Dispatch to Notification Engine & Inbox
        print("\n[TEST 4] Dispatching Broadcast to Notification Subsystem & User Inboxes...")
        cur.execute("UPDATE broadcast_messages SET status = 'PROCESSING' WHERE id = %s;", (bcast_id,))

        cur.execute("SELECT id, user_id, organization_id FROM broadcast_recipients WHERE broadcast_id = %s;", (bcast_id,))
        recipients = cur.fetchall()

        for rec in recipients:
            notif_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO notifications (id, user_id, organization_id, event_name, title, body, priority)
                VALUES (%s, %s, %s, 'ADMIN_BROADCAST_MESSAGE', 'تعطیلی موقت انبارها در روز پنجشنبه', 'به اطلاع می‌رساند...', 'NORMAL');
            """, (notif_id, rec["user_id"], rec["organization_id"]))

            cur.execute("""
                INSERT INTO user_inbox_items (id, user_id, notification_id, title, body, category, is_read)
                VALUES (%s, %s, %s, 'تعطیلی موقت انبارها در روز پنجشنبه', 'به اطلاع می‌رساند...', 'SYSTEM', FALSE);
            """, (str(uuid.uuid4()), rec["user_id"], notif_id))

            cur.execute("""
                UPDATE broadcast_recipients 
                SET notification_id = %s, status = 'SENT'
                WHERE id = %s;
            """, (notif_id, rec["id"]))

        cur.execute("""
            UPDATE broadcast_messages 
            SET status = 'COMPLETED', completed_at = now()
            WHERE id = %s;
        """, (bcast_id,))

        # Verify all 3 recipients have received inbox notifications
        cur.execute("""
            SELECT count(*) as sent_count 
            FROM broadcast_recipients 
            WHERE broadcast_id = %s AND status = 'SENT';
        """, (bcast_id,))
        assert cur.fetchone()["sent_count"] == 3

        cur.execute("SELECT status FROM broadcast_messages WHERE id = %s;", (bcast_id,))
        assert cur.fetchone()["status"] == "COMPLETED"
        print("  [PASS] Broadcast successfully processed: notifications and inboxes created for all recipients.")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL ADMIN BROADCAST TESTS PASSED SUCCESSFULLY!")
        print("================================================================")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_broadcasts()
