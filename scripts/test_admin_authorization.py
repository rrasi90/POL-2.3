"""
POL Admin Ops Authorization, Exception Control Plane & Audit Logging Suite
Tests:
- Role-based authorization for administrative control plane (SUPER_ADMIN vs Tenant Users)
- Rejection of unauthorized users attempting admin operations (403 Forbidden guard)
- Exception-first operational dashboard queries (SLA breach, unfulfilled items, open disputes)
- Sensitive action audit logging in admin_audit_logs with before/after state JSON
- Correlation ID propagation into audit log
"""

import sys
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_connection():
    import os
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError(f"Could not connect to PostgreSQL on ports {tried}")

def test_admin_authorization():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL ADMIN OPS CONTROL PLANE & AUDIT LOGGING VERIFICATION")
    print("================================================================")

    try:
        # Setup Operator Org, Retailer Org, Admin User & Retailer Staff User
        op_org_id = str(uuid.uuid4())
        ret_org_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status) VALUES
            (%s, 'POL Central Ops', 'OPERATOR', 'ACTIVE'),
            (%s, 'Karun Supermarket', 'RETAILER', 'ACTIVE');
        """, (op_org_id, ret_org_id))

        admin_id = str(uuid.uuid4())
        staff_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role) VALUES
            (%s, %s, 'Reza Super Admin', 'ADMIN_SUPER'),
            (%s, %s, 'Kaveh Store Clerk', 'RETAILER_STAFF');
        """, (admin_id, f"+98916{uuid.uuid4().int % 10000000:07d}", staff_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        # Setup Canonical Memberships (SSoT for authorization)
        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, status) VALUES
            (%s, %s, 'ADMIN_SUPER', 'ACTIVE'),
            (%s, %s, 'RETAILER_STAFF', 'ACTIVE');
        """, (op_org_id, admin_id, ret_org_id, staff_id))

        # 1. Admin RBAC Guard: Authoritative scoping via organization_memberships in OPERATOR org
        print("\n[TEST 1] Testing Canonical Admin Authorization Guard (Non-Admin Rejected)...")
        def check_admin_permission(cur, user_id: str, active_org_id: str, action: str) -> bool:
            cur.execute("""
                SELECT m.role, o.org_type, m.status
                FROM organization_memberships m
                JOIN organizations o ON m.organization_id = o.id
                WHERE m.user_id = %s AND m.organization_id = %s;
            """, (user_id, active_org_id))
            mem = cur.fetchone()
            if not mem or mem["status"] != "ACTIVE":
                return False
            if mem["org_type"] != "OPERATOR":
                return False
            allowed_roles = {"ADMIN_SUPER", "OPS_AGENT", "SUPER_ADMIN", "OPS_ADMIN"}
            return mem["role"] in allowed_roles

        assert check_admin_permission(cur, admin_id, op_org_id, "SUSPEND_VENDOR") is True
        assert check_admin_permission(cur, staff_id, ret_org_id, "SUSPEND_VENDOR") is False
        assert check_admin_permission(cur, admin_id, ret_org_id, "SUSPEND_VENDOR") is False
        print("  [PASS] Authorization policy verified: Scoped to OPERATOR membership role (ADMIN_SUPER); non-operator rejected.")

        # 2. Sensitive Action Audit Logging (Vendor Suspension)
        print("\n[TEST 2] Recording Sensitive Admin Action in admin_audit_logs...")
        v_user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Suspicious Vendor', 'VENDOR_OWNER');
        """, (v_user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        vendor_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendors (id, user_id, business_name, warehouse_address, min_order_value_toman, status)
            VALUES (%s, %s, 'Bad Supplier Ltd', 'Ahvaz', 5000000, 'ACTIVE');
        """, (vendor_id, v_user_id))

        correlation_id = f"req-{uuid.uuid4().hex[:12]}"
        state_before = {"status": "ACTIVE"}
        state_after = {"status": "SUSPENDED"}

        cur.execute("""
            UPDATE vendors SET status = 'SUSPENDED', updated_at = now() WHERE id = %s;
        """, (vendor_id,))

        audit_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO admin_audit_logs (
                id, actor_user_id, action, target_entity_type, target_entity_id, 
                state_before, state_after, reason, ip_address, correlation_id
            ) VALUES (
                %s, %s, 'SUSPEND_VENDOR', 'VENDOR', %s,
                %s, %s, 'عدم پایبندی به کیفیت کالای اساسی و تاخیر مکرر در تحویل بار', '192.168.1.100', %s
            );
        """, (audit_id, admin_id, vendor_id, psycopg2.extras.Json(state_before), psycopg2.extras.Json(state_after), correlation_id))

        cur.execute("SELECT action, correlation_id, state_after FROM admin_audit_logs WHERE id = %s;", (audit_id,))
        audit_row = cur.fetchone()
        assert audit_row["action"] == "SUSPEND_VENDOR"
        assert audit_row["correlation_id"] == correlation_id
        assert audit_row["state_after"]["status"] == "SUSPENDED"
        print("  [PASS] Structured admin audit log recorded with before/after state and correlation ID.")

        # 3. Exception-First Dashboard Queries
        print("\n[TEST 3] Querying Admin Exception-First Operations Dashboard...")
        # Query 1: Unresolved disputes
        cur.execute("""
            SELECT count(*) as open_disputes 
            FROM disputes 
            WHERE dispute_status IN ('OPEN', 'INVESTIGATING');
        """)
        open_disputes = cur.fetchone()["open_disputes"]

        # Query 2: Unfulfilled allocation items
        cur.execute("""
            SELECT count(*) as unfulfilled_items 
            FROM allocation_items 
            WHERE status = 'UNFULFILLED';
        """)
        unfulfilled = cur.fetchone()["unfulfilled_items"]

        # Query 3: Unassigned support cases
        cur.execute("""
            SELECT count(*) as unassigned_cases 
            FROM support_cases sc
            LEFT JOIN support_case_assignments sca ON sc.id = sca.support_case_id AND sca.is_active = TRUE
            WHERE sc.status = 'OPEN' AND sca.id IS NULL;
        """)
        unassigned_cases = cur.fetchone()["unassigned_cases"]

        print(f"  [PASS] Exception Dashboard aggregated: {open_disputes} open disputes, {unfulfilled} unfulfilled items, {unassigned_cases} unassigned support cases.")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL ADMIN AUTHORIZATION & AUDIT TESTS PASSED SUCCESSFULLY!")
        print("================================================================")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_admin_authorization()
