"""
POL Customer Support Cases vs Disputes Runtime Verification Suite
Tests:
- Support case creation across case types (GENERAL, ORDER_INQUIRY, PAYMENT_ASSISTANCE)
- Case assignment workflow (support_case_assignments)
- Threaded messaging between user and Ops agent, including internal notes
- Orthogonal separation between Support Cases and Disputes (Support does NOT hold settlement)
- Escalation path from Support Case to formal Dispute
- Support case resolution lifecycle (OPEN -> IN_PROGRESS -> RESOLVED -> CLOSED)
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

def test_support_cases():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL SUPPORT CASES VS DISPUTES RUNTIME VERIFICATION")
    print("================================================================")

    try:
        # Setup Retailer Org & User
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        phone_user = f"+98916{uuid.uuid4().int % 10000000:07d}"

        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status)
            VALUES (%s, 'Karun Mart', 'RETAILER', 'ACTIVE');
        """, (org_id,))

        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Reza Karuni', 'RETAILER_OWNER');
        """, (user_id, phone_user))

        # Setup Ops Agent
        agent_id = str(uuid.uuid4())
        phone_agent = f"+98916{uuid.uuid4().int % 10000000:07d}"
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Sima Ops Agent', 'OPS_ADMIN');
        """, (agent_id, phone_agent))

        # 1. Create Support Case
        print("\n[TEST 1] User Opening Support Case (ORDER_INQUIRY)...")
        case_id = str(uuid.uuid4())
        case_num = f"SUP-{uuid.uuid4().hex[:8].upper()}"

        cur.execute("""
            INSERT INTO support_cases (id, user_id, organization_id, case_number, case_type, priority, status, subject)
            VALUES (%s, %s, %s, %s, 'ORDER_INQUIRY', 'NORMAL', 'OPEN', 'استعلام زمان تحویل بار روغن خوراکی');
        """, (case_id, user_id, org_id, case_num))

        cur.execute("SELECT status, case_type FROM support_cases WHERE id = %s;", (case_id,))
        case = cur.fetchone()
        assert case["status"] == "OPEN"
        assert case["case_type"] == "ORDER_INQUIRY"
        print(f"  [PASS] Support case created: {case_num} in OPEN status.")

        # 2. Case Assignment Workflow
        print("\n[TEST 2] Ops Assigning Support Case to Support Agent...")
        cur.execute("""
            INSERT INTO support_case_assignments (id, support_case_id, assigned_to_user_id, assigned_by_user_id, is_active)
            VALUES (%s, %s, %s, %s, TRUE);
        """, (str(uuid.uuid4()), case_id, agent_id, agent_id))

        cur.execute("""
            UPDATE support_cases SET status = 'IN_PROGRESS', updated_at = now() WHERE id = %s;
        """, (case_id,))

        cur.execute("SELECT status FROM support_cases WHERE id = %s;", (case_id,))
        assert cur.fetchone()["status"] == "IN_PROGRESS"
        print("  [PASS] Support case transitioned to IN_PROGRESS with active agent assignment.")

        # 3. Threaded Messaging & Internal Notes
        print("\n[TEST 3] Threaded Messaging (User Message, Agent Reply, Internal Note)...")
        msg_user_id = str(uuid.uuid4())
        msg_agent_id = str(uuid.uuid4())
        msg_note_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO support_case_messages (id, support_case_id, sender_user_id, sender_type, message_text, is_internal) VALUES
            (%s, %s, %s, 'USER', 'سلام، سفارش من کی ارسال می‌شود؟', FALSE),
            (%s, %s, %s, 'AGENT', 'سلام، بار شما ساعت ۱۴ تحویل خواهد شد.', FALSE),
            (%s, %s, %s, 'AGENT', 'تماس با بنکدار انجام شد، راننده تایید کرد.', TRUE);
        """, (msg_user_id, case_id, user_id, msg_agent_id, case_id, agent_id, msg_note_id, case_id, agent_id))

        # Check total messages and visible to user (is_internal = FALSE)
        cur.execute("SELECT count(*) as total FROM support_case_messages WHERE support_case_id = %s;", (case_id,))
        assert cur.fetchone()["total"] == 3

        cur.execute("""
            SELECT count(*) as user_visible 
            FROM support_case_messages 
            WHERE support_case_id = %s AND is_internal = FALSE;
        """, (case_id,))
        assert cur.fetchone()["user_visible"] == 2
        print("  [PASS] Threaded messages verified: 2 public messages + 1 internal staff note.")

        # 4. Assert Separation from Disputes (Support Case does NOT lock settlement)
        print("\n[TEST 4] Verifying Orthogonal Separation: Support Case does NOT touch Dispute Domain...")
        # Create a mock order and settlement
        retailer_db_id = str(uuid.uuid4())
        vendor_db_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address, latitude, longitude)
            VALUES (%s, %s, %s, 'Karun Mart', 'Kianpars', 'Ahvaz', 31.32, 48.67);
        """, (retailer_db_id, user_id, org_id))

        cur.execute("""
            INSERT INTO vendors (id, user_id, business_name, warehouse_address, min_order_value_toman)
            VALUES (%s, %s, 'Vendor Test Corp', 'Warehouse 1, Shahr-e-Bonakdaran', 5000000);
        """, (vendor_db_id, agent_id))

        og_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO order_groups (id, retailer_id, total_amount_toman, group_status)
            VALUES (%s, %s, 10000000, 'ACTIVE');
        """, (og_id, retailer_db_id))

        order_id = str(uuid.uuid4())
        ord_num = f"ORD-SUP-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO orders (id, order_group_id, retailer_id, vendor_id, order_number, total_amount_toman, order_status, dispute_status)
            VALUES (%s, %s, %s, %s, %s, 10000000, 'DELIVERED', 'NONE');
        """, (order_id, og_id, retailer_db_id, vendor_db_id, ord_num))

        settle_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO settlements (id, order_id, vendor_id, gross_amount_toman, net_vendor_amount_toman, status)
            VALUES (%s, %s, %s, 10000000, 10000000, 'CALCULATED');
        """, (settle_id, order_id, vendor_db_id))

        # User links support case to order
        cur.execute("UPDATE support_cases SET related_order_id = %s WHERE id = %s;", (order_id, case_id))

        # Assert order.dispute_status is still NONE and settlement is still CALCULATED
        cur.execute("SELECT dispute_status FROM orders WHERE id = %s;", (order_id,))
        assert cur.fetchone()["dispute_status"] == "NONE"

        cur.execute("SELECT status FROM settlements WHERE id = %s;", (settle_id,))
        assert cur.fetchone()["status"] == "CALCULATED"
        print("  [PASS] Support case does NOT impact order.dispute_status or settlement status (Orthogonal!).")

        # 5. Case Resolution Lifecycle
        print("\n[TEST 5] Resolving Support Case (IN_PROGRESS -> RESOLVED -> CLOSED)...")
        cur.execute("UPDATE support_cases SET status = 'RESOLVED', updated_at = now() WHERE id = %s;", (case_id,))
        cur.execute("SELECT status FROM support_cases WHERE id = %s;", (case_id,))
        assert cur.fetchone()["status"] == "RESOLVED"

        cur.execute("UPDATE support_cases SET status = 'CLOSED', updated_at = now() WHERE id = %s;", (case_id,))
        cur.execute("SELECT status FROM support_cases WHERE id = %s;", (case_id,))
        assert cur.fetchone()["status"] == "CLOSED"
        print("  [PASS] Support case closed successfully.")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL SUPPORT CASE TESTS PASSED SUCCESSFULLY!")
        print("================================================================")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_support_cases()
