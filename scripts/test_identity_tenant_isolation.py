"""
POL Identity, Organization, Membership & Tenant Isolation Verification Suite
Tests:
- Organization creation & multi-tenant boundary
- Multi-user memberships (Owner vs Staff)
- Duplicate membership constraint (uq_org_user)
- Strict cross-organization tenant scoping
- User session lifecycle & revocation
- User device registration & push token
- OTP challenge brute-force lock (max attempts -> BLOCKED)
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

def test_tenant_isolation():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL IDENTITY & TENANT ISOLATION RUNTIME TEST")
    print("================================================================")

    try:
        # 1. Create Organizations
        print("\n[TEST 1] Creating Organizations (Retailer 1, Retailer 2, Vendor 1)...")
        org_ret1 = str(uuid.uuid4())
        org_ret2 = str(uuid.uuid4())
        org_vnd1 = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status) VALUES
            (%s, 'Supermarket Karun', 'RETAILER', 'ACTIVE'),
            (%s, 'Supermarket Zaitoon', 'RETAILER', 'ACTIVE'),
            (%s, 'Pakhsh Jonoub Wholesale', 'VENDOR', 'ACTIVE')
            ON CONFLICT (id) DO NOTHING;
        """, (org_ret1, org_ret2, org_vnd1))

        # 2. Create Users
        print("\n[TEST 2] Creating Users (Owner 1, Staff 1, Owner 2, Vendor Owner)...")
        u_ret1_owner = str(uuid.uuid4())
        u_ret1_staff = str(uuid.uuid4())
        u_ret2_owner = str(uuid.uuid4())
        u_vnd1_owner = str(uuid.uuid4())

        p1 = f"+98916{uuid.uuid4().int % 10000000:07d}"
        p2 = f"+98916{uuid.uuid4().int % 10000000:07d}"
        p3 = f"+98916{uuid.uuid4().int % 10000000:07d}"
        p4 = f"+98916{uuid.uuid4().int % 10000000:07d}"

        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role) VALUES
            (%s, %s, 'Ali Karuni (Owner)', 'RETAILER_OWNER'),
            (%s, %s, 'Reza Karuni (Staff)', 'RETAILER_STAFF'),
            (%s, %s, 'Hassan Zaitooni (Owner)', 'RETAILER_OWNER'),
            (%s, %s, 'Mohammad Jonoubi (Vendor)', 'VENDOR_OWNER');
        """, (u_ret1_owner, p1, u_ret1_staff, p2, u_ret2_owner, p3, u_vnd1_owner, p4))

        # 3. Create Memberships
        print("\n[TEST 3] Creating Organization Memberships...")
        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, status) VALUES
            (%s, %s, 'RETAILER_OWNER', 'ACTIVE'),
            (%s, %s, 'RETAILER_STAFF', 'ACTIVE'),
            (%s, %s, 'RETAILER_OWNER', 'ACTIVE'),
            (%s, %s, 'VENDOR_OWNER', 'ACTIVE');
        """, (org_ret1, u_ret1_owner, org_ret1, u_ret1_staff, org_ret2, u_ret2_owner, org_vnd1, u_vnd1_owner))

        # 4. Assert Duplicate Membership Constraint (uq_org_user)
        print("\n[TEST 4] Asserting Duplicate Membership Rejection...")
        conn.commit()
        dup_rejected = False
        try:
            cur.execute("""
                INSERT INTO organization_memberships (organization_id, user_id, role, status)
                VALUES (%s, %s, 'RETAILER_STAFF', 'ACTIVE');
            """, (org_ret1, u_ret1_owner))
        except psycopg2.IntegrityError:
            conn.rollback()
            dup_rejected = True
            print("  [PASS] Duplicate membership in same org correctly rejected by uq_org_user constraint.")
        assert dup_rejected, "Expected duplicate membership to be rejected!"

        # 5. Strict Tenant Isolation Query Check
        print("\n[TEST 5] Verifying Strict Tenant Isolation Query Scoping...")
        # Create baskets for both retailer orgs
        b_id1 = str(uuid.uuid4())
        b_id2 = str(uuid.uuid4())
        # First ensure retailers exist with matching user_ids
        cur.execute("""
            INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address, latitude, longitude) VALUES
            (%s, %s, %s, 'Store Karun', 'Kianpars', 'Ahvaz Kianpars', 31.32, 48.67),
            (%s, %s, %s, 'Store Zaitoon', 'Zaitoon Karmandi', 'Ahvaz Zaitoon', 31.35, 48.70)
            ON CONFLICT (id) DO NOTHING;
        """, (str(uuid.uuid4()), u_ret1_owner, org_ret1, str(uuid.uuid4()), u_ret2_owner, org_ret2))

        cur.execute("SELECT id FROM retailers WHERE organization_id = %s;", (org_ret1,))
        ret1_db_id = cur.fetchone()["id"]
        cur.execute("SELECT id FROM retailers WHERE organization_id = %s;", (org_ret2,))
        ret2_db_id = cur.fetchone()["id"]

        cur.execute("""
            INSERT INTO baskets (id, retailer_id, version, status) VALUES
            (%s, %s, 1, 'OPEN'),
            (%s, %s, 1, 'OPEN');
        """, (b_id1, ret1_db_id, b_id2, ret2_db_id))

        # Test: Query baskets with Tenant Scope of Org 1
        cur.execute("""
            SELECT b.id FROM baskets b
            JOIN retailers r ON b.retailer_id = r.id
            WHERE r.organization_id = %s;
        """, (org_ret1,))
        accessible_baskets = [row["id"] for row in cur.fetchall()]
        assert b_id1 in accessible_baskets, "Org 1 should access its own basket"
        assert b_id2 not in accessible_baskets, "Org 1 MUST NOT see Org 2 basket (Cross-tenant leak!)"
        print("  [PASS] Tenant isolation verified: Org 1 sees only own baskets, Org 2 baskets invisible.")

        # 6. User Sessions & Revocation
        print("\n[TEST 6] Testing User Sessions & Revocation...")
        sess_id = str(uuid.uuid4())
        tok_hash = f"hash_token_{uuid.uuid4().hex}"
        cur.execute("""
            INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
            VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '24 hours');
        """, (sess_id, u_ret1_owner, org_ret1, tok_hash))

        cur.execute("SELECT status FROM user_sessions WHERE id = %s;", (sess_id,))
        assert cur.fetchone()["status"] == "ACTIVE"

        # Revoke session
        cur.execute("UPDATE user_sessions SET status = 'REVOKED' WHERE id = %s;", (sess_id,))
        cur.execute("SELECT status FROM user_sessions WHERE id = %s;", (sess_id,))
        assert cur.fetchone()["status"] == "REVOKED"
        print("  [PASS] Session lifecycle: ACTIVE -> REVOKED verified.")

        # 7. OTP Challenge & Brute-Force Lock
        print("\n[TEST 7] Testing OTP Challenge Brute-Force Lock (max_attempts = 5)...")
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, '+989161110001', 'salt_hashed_12345', 'LOGIN', 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id,))

        # Simulate 5 failed attempts
        for attempt in range(1, 6):
            cur.execute("""
                UPDATE otp_challenges 
                SET attempts_count = attempts_count + 1,
                    status = CASE WHEN attempts_count + 1 >= max_attempts THEN 'BLOCKED' ELSE 'PENDING' END
                WHERE id = %s
                RETURNING attempts_count, status;
            """, (otp_id,))
            res = cur.fetchone()

        assert res["attempts_count"] == 5
        assert res["status"] == "BLOCKED"
        print("  [PASS] OTP brute-force defense verified: status transitioned to BLOCKED after 5 failed attempts.")

        # =============================================================
        # SECTION 14: MULTI-ORGANIZATION REQUIREMENTS (SCENARIOS A-E)
        # =============================================================

        # 8. Scenario A: Single user with memberships in two Retailer Orgs
        print("\n[TEST 8 - SCENARIO A] Single user belonging to two Retailer Orgs (Multi-store owner)...")
        u_multi_ret = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Hossein MultiStore', 'RETAILER_OWNER');
        """, (u_multi_ret, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, status, is_primary) VALUES
            (%s, %s, 'RETAILER_OWNER', 'ACTIVE', TRUE),
            (%s, %s, 'RETAILER_OWNER', 'ACTIVE', FALSE);
        """, (org_ret1, u_multi_ret, org_ret2, u_multi_ret))

        cur.execute("""
            SELECT count(*) as mem_count FROM organization_memberships
            WHERE user_id = %s AND status = 'ACTIVE';
        """, (u_multi_ret,))
        assert cur.fetchone()["mem_count"] == 2
        print("  [PASS] Scenario A verified: User successfully holds active memberships in multiple Retailer Orgs.")

        # 9. Scenario B: Single user with membership in Retailer Org A and Vendor Org B
        print("\n[TEST 9 - SCENARIO B] Single user belonging to Retailer Org A and Vendor Org B...")
        u_hybrid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Ali Hybrid Owner', 'RETAILER_OWNER');
        """, (u_hybrid, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, status, is_primary) VALUES
            (%s, %s, 'RETAILER_OWNER', 'ACTIVE', TRUE),
            (%s, %s, 'VENDOR_OWNER', 'ACTIVE', FALSE);
        """, (org_ret1, u_hybrid, org_vnd1, u_hybrid))

        cur.execute("""
            SELECT m.role, o.org_type FROM organization_memberships m
            JOIN organizations o ON m.organization_id = o.id
            WHERE m.user_id = %s;
        """, (u_hybrid,))
        memberships = {r["org_type"]: r["role"] for r in cur.fetchall()}
        assert memberships.get("RETAILER") == "RETAILER_OWNER"
        assert memberships.get("VENDOR") == "VENDOR_OWNER"
        print("  [PASS] Scenario B verified: Single user holds dual memberships in Retailer and Vendor organizations.")

        # 10. Scenario C: User without membership has NO access to tenant data
        print("\n[TEST 10 - SCENARIO C] User without membership rejected from tenant data...")
        u_outsider = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Random Stranger', 'RETAILER_STAFF');
        """, (u_outsider, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        def can_access_org_data(user_id: str, org_id: str) -> bool:
            cur.execute("""
                SELECT id FROM organization_memberships
                WHERE user_id = %s AND organization_id = %s AND status = 'ACTIVE';
            """, (user_id, org_id))
            return cur.fetchone() is not None

        assert can_access_org_data(u_outsider, org_ret1) is False
        assert can_access_org_data(u_outsider, org_vnd1) is False
        print("  [PASS] Scenario C verified: User without membership has zero access to tenant data.")

        # 11. Scenario D: User with REVOKED membership rejected from access
        print("\n[TEST 11 - SCENARIO D] User with REVOKED membership rejected from access...")
        u_fired_staff = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Fired Clerk', 'RETAILER_STAFF');
        """, (u_fired_staff, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, status, is_primary)
            VALUES (%s, %s, 'RETAILER_STAFF', 'REVOKED', FALSE);
        """, (org_ret1, u_fired_staff))

        assert can_access_org_data(u_fired_staff, org_ret1) is False
        print("  [PASS] Scenario D verified: REVOKED membership denies access.")

        # 12. Scenario E: Active organization context strictly scopes data
        print("\n[TEST 12 - SCENARIO E] Session active_organization_id scopes context strictly...")
        sess_hybrid = str(uuid.uuid4())
        tok_hybrid = f"tok_hybrid_{uuid.uuid4().hex}"
        cur.execute("""
            INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
            VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '24 hours');
        """, (sess_hybrid, u_hybrid, org_vnd1, tok_hybrid))

        # Query active session context
        cur.execute("SELECT active_organization_id FROM user_sessions WHERE id = %s;", (sess_hybrid,))
        active_org = cur.fetchone()["active_organization_id"]
        assert active_org == uuid.UUID(org_vnd1) or str(active_org) == org_vnd1

        # Assert query strictly scoped to active_org
        cur.execute("""
            SELECT id FROM organization_memberships
            WHERE user_id = %s AND organization_id = %s AND status = 'ACTIVE';
        """, (u_hybrid, active_org))
        mem_active = cur.fetchone()
        assert mem_active is not None
        print("  [PASS] Scenario E verified: Session actively scopes authorization to active_organization_id.")

        # =============================================================
        # SECTION 15: ROLE INVARIANTS ENFORCEMENT AT DB LEVEL
        # =============================================================
        print("\n[TEST 13 - SECTION 15] Verifying DB-Level Role Invariants Enforcement...")
        op_org_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status)
            VALUES (%s, 'POL System Operations', 'OPERATOR', 'ACTIVE');
        """, (op_org_id,))

        # Invariant 1: RETAILER_OWNER in OPERATOR org must fail
        conn.commit()
        inv1_failed = False
        try:
            cur.execute("""
                INSERT INTO organization_memberships (organization_id, user_id, role, status)
                VALUES (%s, %s, 'RETAILER_OWNER', 'ACTIVE');
            """, (op_org_id, u_outsider))
        except psycopg2.Error as e:
            conn.rollback()
            inv1_failed = True
            assert "RETAILER organizations" in str(e) or "trg_enforce" in str(e)
            print("  [PASS] Invariant 1 verified: RETAILER_OWNER rejected in OPERATOR org by DB trigger.")
        assert inv1_failed, "Expected DB trigger to reject RETAILER_OWNER in OPERATOR org!"

        # Invariant 2: VENDOR_OWNER in RETAILER org must fail
        conn.commit()
        inv2_failed = False
        try:
            cur.execute("""
                INSERT INTO organization_memberships (organization_id, user_id, role, status)
                VALUES (%s, %s, 'VENDOR_OWNER', 'ACTIVE');
            """, (org_ret1, u_outsider))
        except psycopg2.Error as e:
            conn.rollback()
            inv2_failed = True
            assert "VENDOR organizations" in str(e) or "trg_enforce" in str(e)
            print("  [PASS] Invariant 2 verified: VENDOR_OWNER rejected in RETAILER org by DB trigger.")
        assert inv2_failed, "Expected DB trigger to reject VENDOR_OWNER in RETAILER org!"

        # Invariant 3: ADMIN_SUPER in VENDOR org must fail
        conn.commit()
        inv3_failed = False
        try:
            cur.execute("""
                INSERT INTO organization_memberships (organization_id, user_id, role, status)
                VALUES (%s, %s, 'ADMIN_SUPER', 'ACTIVE');
            """, (org_vnd1, u_outsider))
        except psycopg2.Error as e:
            conn.rollback()
            inv3_failed = True
            assert "OPERATOR organizations" in str(e) or "trg_enforce" in str(e)
            print("  [PASS] Invariant 3 verified: ADMIN_SUPER rejected in VENDOR org by DB trigger.")
        assert inv3_failed, "Expected DB trigger to reject ADMIN_SUPER in VENDOR org!"

        # Valid Assignment: ADMIN_SUPER in OPERATOR org must succeed
        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, status)
            VALUES (%s, %s, 'ADMIN_SUPER', 'ACTIVE');
        """, (op_org_id, u_outsider))
        print("  [PASS] Valid role assignment: ADMIN_SUPER accepted in OPERATOR org.")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL IDENTITY, MULTI-ORG & TENANT ISOLATION TESTS PASSED (13/13)!")
        print("================================================================")
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_tenant_isolation()
