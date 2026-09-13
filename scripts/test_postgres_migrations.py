"""
POL Platform Canonical PostgreSQL 18 Migration Verification Harness
Validates migrations/001_initial_schema.sql against real PostgreSQL 18:
- Executes clean migration on PostgreSQL 18
- Asserts all 37 canonical domain tables are present in public schema
- Asserts critical indexes, foreign keys, and check constraints
- Asserts D-014 Multi-Vendor and NON_CUSTODIAL_DIRECT constraints
"""

import os
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

def reset_and_migrate(conn):
    dsn = conn.get_dsn_parameters()
    actual_db = dsn.get("dbname", "")
    if actual_db != "pol_test":
        raise RuntimeError(f"Destructive reset BLOCKED: dbname '{actual_db}' is not 'pol_test'!")
    print("Resetting public schema and executing migrations/001_initial_schema.sql...")
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    conn.commit()

    with open(MIGRATION_FILE, "r", encoding="utf-8") as f:
        sql_content = f.read()

    cur.execute(sql_content)
    conn.commit()
    print("Initial migration (001) executed successfully.")

    migration_file_2 = os.path.join(REPO_ROOT, "migrations", "002_platform_core_schema.sql")
    if os.path.exists(migration_file_2):
        with open(migration_file_2, "r", encoding="utf-8") as f:
            sql_content_2 = f.read()
        cur.execute(sql_content_2)
        conn.commit()
        print("Platform core migration (002) executed successfully.")

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

def main():
    print("================================================================")
    print("POL CANONICAL POSTGRESQL 18 MIGRATION VERIFICATION")
    print("================================================================")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        pg_ver = cur.fetchone()[0]
        print(f"Connected to PostgreSQL: {pg_ver}")
        assert "PostgreSQL 18" in pg_ver, f"Expected PostgreSQL 18, got: {pg_ver}"

        reset_and_migrate(conn)
        verify_tables(conn)
        verify_constraints(conn)
        verify_foreign_keys_and_indexes(conn)

        conn.close()
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
