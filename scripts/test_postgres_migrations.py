"""
POL Platform Canonical PostgreSQL 18 Migration Verification Harness
Validates migrations/001_initial_schema.sql against real PostgreSQL 18:
- Executes clean migration on PostgreSQL 18
- Asserts all 37 canonical domain tables are present in public schema
- Asserts critical indexes, foreign keys, and check constraints
- Asserts D-014 Multi-Vendor and NON_CUSTODIAL_DIRECT constraints
"""

import os
from uuid import uuid4
import sys
import psycopg2
from psycopg2 import sql

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MIGRATION_FILE = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")

DB_CONFIG = {
    "dbname": "pol_test",
    "user": "postgres",
    "host": "127.0.0.1",
}

EXPECTED_37_TABLES = {
    "users",
    "retailers",
    "vendors",
    "brands",
    "categories",
    "subcategories",
    "products",
    "product_reference_metadata",
    "product_identifiers",
    "media_assets",
    "product_media",
    "product_candidates",
    "product_merge_history",
    "vendor_products",
    "vendor_inventory",
    "vendor_prices",
    "inventory_audit_log",
    "baskets",
    "basket_items",
    "allocation_plans",
    "allocation_items",
    "order_groups",
    "orders",
    "order_items",
    "deliveries",
    "delivery_attempts",
    "proof_of_delivery",
    "disputes",
    "payments",
    "payment_attempts",
    "settlements",
    "settlement_adjustments",
    "refunds",
    "reputations",
    "reputation_snapshots",
    "outbox_events",
    "domain_events_log"
}

def get_connection():
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    last_err = None
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            cfg = dict(DB_CONFIG, port=p)
            conn = psycopg2.connect(**cfg)
            conn.autocommit = False
            return conn
        except Exception as e:
            last_err = e
    raise last_err

sys.path.insert(0, REPO_ROOT)
from scripts.migration_runner import get_migration_chain, apply_migration_chain, reset_schema, get_connection as runner_get_connection

def get_connection():
    conn, _ = runner_get_connection("pol_test")
    return conn

def reset_and_migrate(conn):
    print("Resetting public schema and executing canonical dynamic migration chain...")
    reset_schema(conn, "pol_test")
    chain = get_migration_chain()
    applied, table_count = apply_migration_chain(conn, chain, verbose=True)
    print(f"Dynamic migration chain ({len(applied)} migrations) executed successfully. Total tables: {table_count}")
    return applied

def run_upgrade_test(conn):
    """
    Section 9: Explicit Upgrade Test.
    Simulates existing database with 001 + 002, then executes upgrade migration 003.
    Verifies that schema evolution succeeds smoothly.
    """
    print("\n[UPGRADE TEST] Testing incremental schema upgrade path (001 -> 002 -> 003)...")
    reset_schema(conn, "pol_test")
    chain = get_migration_chain()

    # Step 1: Apply initial and core migrations
    base_chain = [m for m in chain if "001" in m or "002" in m]
    upgrade_migrations = [m for m in chain if m not in base_chain]

    print(f"Applying base chain: {[os.path.basename(m) for m in base_chain]}...")
    apply_migration_chain(conn, base_chain, verbose=False)

    # Step 2: Apply subsequent upgrade migrations (003, ...)
    for up_mig in upgrade_migrations:
        print(f"Upgrading with {os.path.basename(up_mig)}...")
        apply_migration_chain(conn, [up_mig], verbose=True)

    print("[PASS] Incremental upgrade path verified successfully.")


EXPECTED_19_PLATFORM_TABLES = {
    "organizations",
    "organization_memberships",
    "user_devices",
    "user_sessions",
    "otp_challenges",
    "notifications",
    "notification_deliveries",
    "user_inbox_items",
    "notification_preferences",
    "broadcast_messages",
    "broadcast_recipients",
    "support_cases",
    "support_case_messages",
    "support_case_assignments",
    "field_tasks",
    "inventory_reservations",
    "invoices",
    "invoice_items",
    "admin_audit_logs"
}

EXPECTED_56_TABLES = EXPECTED_37_TABLES | EXPECTED_19_PLATFORM_TABLES

def verify_tables(conn):
    print("\n[VERIFICATION 1] Verifying all 56 canonical + platform tables in public schema...")
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE';
    """)
    tables = {row[0] for row in cur.fetchall()}
    
    missing = EXPECTED_56_TABLES - tables
    extra = tables - EXPECTED_56_TABLES

    print(f"Total tables found: {len(tables)} (Expected: {len(EXPECTED_56_TABLES)})")
    if missing:
        raise AssertionError(f"Missing expected tables: {missing}")
    if extra:
        print(f"Note: additional tables present: {extra}")
    assert len(tables) >= 56, f"Expected at least 56 tables, found {len(tables)}"
    print("[PASS] All 56 canonical + platform tables verified present.")

def verify_constraints(conn):
    print("\n[VERIFICATION 2] Verifying domain CHECK constraints and architecture rules...")
    cur = conn.cursor()

    # 1. Check order_status does NOT contain DISPUTED
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'orders'::regclass AND contype = 'c';
    """)
    constraints = cur.fetchall()
    order_status_check = [c[1] for c in constraints if "order_status" in c[1]]
    assert len(order_status_check) > 0, "order_status CHECK constraint missing on orders table"
    assert "DISPUTED" not in order_status_check[0], (
        f"ARCHITECTURAL VIOLATION: 'DISPUTED' must not be in orders.order_status! Found: {order_status_check[0]}"
    )
    print(" - orders.order_status correctly excludes 'DISPUTED'")

    # 2. Check orders.dispute_status exists with allowed values
    dispute_status_check = [c[1] for c in constraints if "dispute_status" in c[1]]
    assert len(dispute_status_check) > 0, "dispute_status CHECK constraint missing on orders table"
    print(" - orders.dispute_status projection CHECK verified")

    # 3. Check custody_model in payments allows NON_CUSTODIAL_DIRECT
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'payments'::regclass AND contype = 'c';
    """)
    pay_constraints = cur.fetchall()
    custody_check = [c[1] for c in pay_constraints if "custody_model" in c[1]]
    assert len(custody_check) > 0, "custody_model CHECK constraint missing on payments table"
    assert "NON_CUSTODIAL_DIRECT" in custody_check[0], (
        f"ARCHITECTURAL VIOLATION: NON_CUSTODIAL_DIRECT missing in payments! Found: {custody_check[0]}"
    )
    print(" - payments.custody_model enforces NON_CUSTODIAL_DIRECT")

    # 4. Check allocation_plans strategy default
    cur.execute("""
        SELECT column_name, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'allocation_plans' AND column_name = 'strategy';
    """)
    row = cur.fetchone()
    assert row is not None, "strategy column missing in allocation_plans"
    assert "MULTI_VENDOR_MIN_FRAGMENTATION" in row[1], (
        f"Expected strategy default MULTI_VENDOR_MIN_FRAGMENTATION, got: {row[1]}"
    )
    print(" - allocation_plans.strategy defaults to MULTI_VENDOR_MIN_FRAGMENTATION")

    # 5. Check organization_memberships canonical roles (ADMIN_SUPER, OPS_AGENT)
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'organization_memberships'::regclass AND contype = 'c';
    """)
    mem_constraints = cur.fetchall()
    role_check = [c[1] for c in mem_constraints if "role" in c[1]]
    assert len(role_check) > 0, "role CHECK constraint missing on organization_memberships"
    assert "ADMIN_SUPER" in role_check[0] and "OPS_AGENT" in role_check[0], (
        f"Canonical roles ADMIN_SUPER/OPS_AGENT missing in organization_memberships! Found: {role_check[0]}"
    )
    print(" - organization_memberships enforces canonical roles (ADMIN_SUPER, OPS_AGENT)")

    # 6. Check role invariant trigger exists
    cur.execute("""
        SELECT tgname FROM pg_trigger
        WHERE tgrelid = 'organization_memberships'::regclass
          AND tgname = 'trg_enforce_org_membership_role_invariant';
    """)
    assert cur.fetchone() is not None, "trg_enforce_org_membership_role_invariant trigger missing on organization_memberships"
    print(" - trg_enforce_org_membership_role_invariant trigger verified")

    # 7. Check allocation_plans status accepts SUPERSEDED
    cur.execute("""
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid = 'allocation_plans'::regclass AND contype = 'c';
    """)
    alloc_constraints = cur.fetchall()
    status_check = [c[1] for c in alloc_constraints if "status" in c[1]]
    assert len(status_check) > 0, "status CHECK constraint missing on allocation_plans"
    assert "SUPERSEDED" in status_check[0], (
        f"Status SUPERSEDED missing in allocation_plans! Found: {status_check[0]}"
    )
    print(" - allocation_plans.status supports 'SUPERSEDED'")

def verify_foreign_keys_and_indexes(conn):
    print("\n[VERIFICATION 3] Verifying foreign keys and critical indexes...")
    cur = conn.cursor()

    # Check foreign keys from settlement_adjustments to disputes
    cur.execute("""
        SELECT tc.constraint_name, ccu.table_name AS foreign_table_name, kcu.column_name 
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
          AND tc.table_name = 'settlement_adjustments';
    """)
    fks = cur.fetchall()
    fk_targets = {row[1] for row in fks}
    assert "disputes" in fk_targets, "settlement_adjustments missing FK to disputes"
    assert "settlements" in fk_targets, "settlement_adjustments missing FK to settlements"
    print(" - settlement_adjustments FKs to disputes and settlements verified")

    # Check refunds FK to disputes
    cur.execute("""
        SELECT tc.constraint_name, ccu.table_name AS foreign_table_name, kcu.column_name 
        FROM information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' 
          AND tc.table_name = 'refunds';
    """)
    refund_fks = cur.fetchall()
    refund_fk_targets = {row[1] for row in refund_fks}
    assert "disputes" in refund_fk_targets, "refunds missing FK to disputes"
    assert "orders" in refund_fk_targets, "refunds missing FK to orders"
    print(" - refunds FKs to disputes and orders verified")

    # Check partial unique index uq_vendor_product_current_price
    cur.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'vendor_prices' 
          AND indexname = 'uq_vendor_product_current_price';
    """)
    idx = cur.fetchone()
    assert idx is not None, "uq_vendor_product_current_price index missing on vendor_prices"
    assert "is_current = true" in idx[1].lower(), f"Expected partial unique index on is_current = true, got: {idx[1]}"
    print(" - uq_vendor_product_current_price partial unique index verified")

    # Check partial unique index uq_user_primary_membership
    cur.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'organization_memberships' 
          AND indexname = 'uq_user_primary_membership';
    """)
    idx_m = cur.fetchone()
    assert idx_m is not None, "uq_user_primary_membership index missing"
    assert "is_primary = true" in idx_m[1].lower(), f"Expected is_primary = true partial index, got {idx_m[1]}"
    print(" - uq_user_primary_membership partial unique index verified")

    # Check partial unique index uq_active_support_assignment
    cur.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'support_case_assignments' 
          AND indexname = 'uq_active_support_assignment';
    """)
    idx_s = cur.fetchone()
    assert idx_s is not None, "uq_active_support_assignment index missing"
    assert "is_active = true" in idx_s[1].lower(), f"Expected is_active = true partial index, got {idx_s[1]}"
    print(" - uq_active_support_assignment partial unique index verified")

    # Check partial unique index for pending vendor barcode candidates (migration 046)
    cur.execute("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'product_candidates'
          AND indexname = 'uq_product_candidates_pending_vendor_barcode';
    """)
    idx_c = cur.fetchone()
    assert idx_c is not None, "uq_product_candidates_pending_vendor_barcode index missing"
    idx_c_def = idx_c[1].lower()
    assert "vendor_id" in idx_c_def and "barcode" in idx_c_def, (
        f"Expected vendor_id+barcode candidate guard, got: {idx_c[1]}"
    )
    assert "status = 'pending_review'" in idx_c_def, (
        f"Expected PENDING_REVIEW predicate, got: {idx_c[1]}"
    )
    print(" - pending vendor barcode concurrency index verified")

    # Check organization_id columns on retailers and vendors
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'retailers' AND column_name = 'organization_id';
    """)
    assert cur.fetchone() is not None, "organization_id missing on retailers"
    cur.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'vendors' AND column_name = 'organization_id';
    """)
    assert cur.fetchone() is not None, "organization_id missing on vendors"
    print(" - retailers and vendors canonical organization_id verified")

def verify_delegated_permission_schema(conn):
    """Verify migration 047 D-026/VD-15 schema invariants."""
    cur = conn.cursor()

    for table in ("delegated_permission_grants", "permission_audit_events"):
        cur.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema='public' AND table_name=%s
            """,
            (table,),
        )
        assert cur.fetchone() is not None, f"{table} table missing after migration 047"

    cur.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE tablename='delegated_permission_grants'
          AND indexname='idx_delegated_permission_active'
        """
    )
    assert cur.fetchone() is not None, "active delegated-permission index missing"

    cur.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE tablename='delegated_permission_grants'
          AND indexname='uq_delegated_permission_membership_key'
        """
    )
    assert cur.fetchone() is not None, "delegated-permission membership/key uniqueness missing"

    cur.execute(
        """
        SELECT tgname
        FROM pg_trigger
        WHERE tgrelid='permission_audit_events'::regclass
          AND tgname='trg_permission_audit_no_update'
        """
    )
    assert cur.fetchone() is not None, "permission audit append-only trigger missing"

    cur.execute(
        """
        SELECT conname, pg_get_constraintdef(oid)
        FROM pg_constraint
        WHERE conrelid='delegated_permission_grants'::regclass
          AND contype='c'
        """
    )
    grant_checks = " ".join(row[1].lower() for row in cur.fetchall())
    assert "granted" in grant_checks and "revoked" in grant_checks, "grant status CHECK missing"
    assert "inventory.scan" in grant_checks and "membership.manage" in grant_checks, (
        "canonical delegated permission keys missing from DB CHECK"
    )

    print(" - migration 047 delegated permission tables, uniqueness, permission keys, and append-only audit guard verified")
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='media_assets'
          AND column_name IN ('upload_target_type','upload_target_id')
        ORDER BY column_name
        """
    )
    media_target_columns = [row[0] for row in cur.fetchall()]
    assert media_target_columns == ["upload_target_id", "upload_target_type"], (
        "migration 048 media target binding columns missing"
    )
    cur.execute(
        """
        SELECT indexname
        FROM pg_indexes
        WHERE tablename='media_assets'
          AND indexname='idx_media_assets_upload_target'
        """
    )
    assert cur.fetchone() is not None, "media upload-target binding index missing"

    cur.close()


def verify_financial_dispute_remediation(conn):
    """Verify migrations 058-062 are present and protect their new invariants."""
    cur = conn.cursor()

    for table in ("dispute_events", "dispute_items"):
        cur.execute(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_schema='public' AND table_name=%s
            """,
            (table,),
        )
        assert cur.fetchone() is not None, f"{table} missing after financial/dispute remediation"

    for table, column in (
        ("disputes", "idempotency_key"),
        ("disputes", "idempotency_fingerprint"),
        ("disputes", "created_by_user_id"),
        ("refunds", "idempotency_key"),
        ("refunds", "idempotency_fingerprint"),
        ("refunds", "approved_at"),
        ("refunds", "completed_by_user_id"),
        ("refunds", "created_by_user_id"),
        ("refunds", "source_type"),
        ("settlement_adjustments", "refund_id"),
        ("payment_evidence", "evidence_media_id"),
    ):
        cur.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s AND column_name=%s
            """,
            (table, column),
        )
        assert cur.fetchone() is not None, f"{table}.{column} missing"

    for table, index_name in (
        ("disputes", "uq_dispute_idempotency_key"),
        ("refunds", "uq_refund_idempotency_key"),
        ("refunds", "uq_refund_per_dispute_v063"),
        ("refunds", "uq_refund_per_return_v063"),
        ("settlement_adjustments", "uq_refund_settlement_adjustment_v058"),
        ("payment_evidence", "idx_payment_evidence_media_v064"),
    ):
        cur.execute(
            "SELECT 1 FROM pg_indexes WHERE tablename=%s AND indexname=%s",
            (table, index_name),
        )
        assert cur.fetchone() is not None, f"Index {index_name} missing"

    for table, constraint_name in (
        ("media_assets", "chk_media_asset_checksum_required_v070"),
        ("deliveries", "chk_delivery_otp_attempt_count_max_v068"),
        ("deliveries", "chk_delivery_otp_format_v068"),
        ("order_items", "chk_order_item_accepted_quantity_v068"),
        ("order_items", "chk_order_item_delivered_quantity_v068"),
    ):
        cur.execute(
            """
            SELECT 1
            FROM pg_constraint
            WHERE conrelid=%s::regclass AND conname=%s
            """,
            (table, constraint_name),
        )
        assert cur.fetchone() is not None, f"Constraint {constraint_name} missing"

    for table, trigger_name in (
        ("dispute_events", "trg_dispute_events_append_only_v058"),
        ("disputes", "trg_validate_dispute_adjudication_v062"),
        ("refunds", "trg_completed_refund_payment_v058"),
        ("payment_evidence", "trg_validate_payment_evidence_media_v064"),
    ):
        cur.execute(
            """
            SELECT 1 FROM pg_trigger
            WHERE tgrelid=%s::regclass AND tgname=%s
            """,
            (table, trigger_name),
        )
        assert cur.fetchone() is not None, f"Trigger {trigger_name} missing"

    cur.execute(
        """
        SELECT 1
        FROM notification_templates
        WHERE event_name='REFUND_COMPLETED'
          AND channel='INBOX'
          AND enabled=TRUE
        LIMIT 1
        """
    )
    assert cur.fetchone() is not None, "REFUND_COMPLETED notification template missing"

    cur.close()
    print(" - financial/dispute remediation 058-062 schema, indexes, triggers and template verified")


def test_dispute_resolution_invariant_direct_sql(conn):
    """Exercise the PostgreSQL adjudication guard directly with a minimal aggregate."""
    cur = conn.cursor()

    # Build only the minimum FK-compatible aggregate. Session trigger replication
    # is disabled locally while creating the order because its parent group belongs
    # to checkout-time concerns outside this focused migration invariant test.
    cur.execute("SET LOCAL session_replication_role = replica")

    cur.execute(
        """
        INSERT INTO organizations (id,name,org_type,status)
        VALUES
            (gen_random_uuid(),'Migration Test Retailer Org','RETAILER','ACTIVE'),
            (gen_random_uuid(),'Migration Test Vendor Org','VENDOR','ACTIVE')
        RETURNING id, org_type
        """
    )
    orgs = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute(
        """
        INSERT INTO users (id,phone_number,full_name,role,is_active)
        VALUES
            (gen_random_uuid(),%s,'Migration Retailer','RETAILER_OWNER',TRUE),
            (gen_random_uuid(),%s,'Migration Vendor','VENDOR_OWNER',TRUE)
        RETURNING id, role
        """,
        (
            f"+989{int.from_bytes(os.urandom(4),'big') % 1000000000:09d}",
            f"+989{int.from_bytes(os.urandom(4),'big') % 1000000000:09d}",
        ),
    )
    users = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute(
        """
        INSERT INTO retailers
            (id,user_id,organization_id,store_name,neighborhood,address,city)
        VALUES
            (gen_random_uuid(),%s,%s,'Migration Test Retailer','Central','Test Address','Ahvaz')
        RETURNING id
        """,
        (users["RETAILER_OWNER"], orgs["RETAILER"]),
    )
    retailer = cur.fetchone()[0]

    cur.execute(
        """
        INSERT INTO vendors
            (id,user_id,organization_id,business_name,warehouse_address,cluster_location)
        VALUES
            (gen_random_uuid(),%s,%s,'Migration Test Vendor','Test Warehouse','Ahvaz')
        RETURNING id
        """,
        (users["VENDOR_OWNER"], orgs["VENDOR"]),
    )
    vendor = cur.fetchone()[0]

    cur.execute(
        """
        INSERT INTO orders
            (id,order_number,retailer_id,vendor_id,order_status,dispute_status,total_amount_toman)
        VALUES
            (gen_random_uuid(),%s,%s,%s,'DELIVERED','NONE',100000)
        RETURNING id
        """,
        (f"MIG-{uuid4().hex[:12]}", retailer, vendor),
    )
    order_id = cur.fetchone()[0]

    # Re-enable normal trigger behavior before testing the remediation trigger.
    cur.execute("SET LOCAL session_replication_role = origin")

    cur.execute(
        """
        INSERT INTO media_assets
            (id,storage_key,file_size_bytes,status,provenance,uploaded_by_user_id)
        VALUES (gen_random_uuid(),%s,1024,'READY','POL_OWNED',%s)
        RETURNING id
        """,
        (f"migration-test/{uuid4().hex}.jpg", users["RETAILER_OWNER"]),
    )
    evidence_id = cur.fetchone()[0]

    with pytest.raises(psycopg2.errors.CheckViolation, match="DISPUTE_APPROVED_AMOUNT_OUT_OF_BOUNDS"):
        cur.execute(
            """
            INSERT INTO disputes (
                id,order_id,retailer_id,vendor_id,dispute_status,
                claimed_amount_toman,approved_amount_toman,resolution_outcome,
                evidence_media_id
            )
            VALUES (gen_random_uuid(),%s,%s,%s,'RESOLVED',1000,2000,'ADJUSTED_SHORTAGE',%s)
            """,
            (order_id, retailer, vendor, evidence_id),
        )

    conn.rollback()
    cur.close()



def test_postgres_migrations():
    """Canonical test entry point for pytest."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT version();")
    pg_ver = cur.fetchone()[0]
    print(f"Connected to PostgreSQL: {pg_ver}")
    assert "PostgreSQL 18" in pg_ver, f"Expected PostgreSQL 18, got: {pg_ver}"

    # Path 1: Clean/Fresh install (001 -> 002 -> 003 -> ...)
    reset_and_migrate(conn)
    verify_tables(conn)
    verify_constraints(conn)
    verify_foreign_keys_and_indexes(conn)
    verify_delegated_permission_schema(conn)
    verify_financial_dispute_remediation(conn)

    # Path 2: Incremental upgrade (001+002, then 003)
    run_upgrade_test(conn)
    verify_tables(conn)
    verify_constraints(conn)
    verify_foreign_keys_and_indexes(conn)
    verify_delegated_permission_schema(conn)
    verify_financial_dispute_remediation(conn)

    conn.close()

def main():
    print("================================================================")
    print("POL CANONICAL POSTGRESQL 18 MIGRATION VERIFICATION")
    print("================================================================")
    try:
        test_postgres_migrations()
        print("\n================================================================")
        print("ALL CANONICAL MIGRATION TESTS PASSED SUCCESSFULLY (56/56 TABLES)")
        print("================================================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[MIGRATION TEST FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
