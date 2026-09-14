#!/usr/bin/env python3
"""
POL Environment & Bootstrap Verifier
Validates:
1. Python version >= 3.11
2. Required packages (psycopg2, pytest)
3. SQL migration chain availability & readability
4. PostgreSQL 18.x connection & port availability
5. Target database 'pol_test' readiness
6. Core tables (56 active tables) & trigger invariants
"""

import os
import sys
import json
import argparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPECTED_MIGRATIONS = [
    "001_initial_schema.sql",
    "002_platform_core_schema.sql",
    "003_contract_reconciliation.sql",
    "004_operational_intelligence.sql",
]
EXPECTED_TABLE_COUNT = 62
EXPECTED_CORE_TABLES = [
    "users",
    "organizations",
    "organization_memberships",
    "user_sessions",
    "user_devices",
    "retailers",
    "vendors",
    "products",
    "vendor_products",
    "vendor_inventory",
    "vendor_prices",
    "baskets",
    "basket_items",
    "allocation_plans",
    "allocation_items",
    "order_groups",
    "orders",
    "order_items",
    "payments",
    "deliveries",
    "settlements",
    "disputes",
    "support_cases",
    "invoices",
    "invoice_items",
    "notifications",
    "user_inbox_items",
    "outbox_events",
    "daily_inventory_confirmations",
    "daily_inventory_confirmation_items",
    "feedback_submissions",
    "vendor_reliability_events",
    "product_identity_lifecycle_logs",
    "returns",
]

def verify_python():
    version_info = sys.version_info
    ver_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    passed = version_info >= (3, 11)
    return {
        "check": "python_version",
        "passed": passed,
        "detail": ver_str,
        "requirement": ">= 3.11",
    }

def verify_dependencies():
    missing = []
    installed = {}
    for pkg in ["psycopg2", "pytest"]:
        try:
            mod = __import__(pkg)
            installed[pkg] = getattr(mod, "__version__", "installed")
        except ImportError:
            missing.append(pkg)
    return {
        "check": "python_dependencies",
        "passed": len(missing) == 0,
        "installed": installed,
        "missing": missing,
    }

def verify_migration_files():
    migrations_dir = os.path.join(REPO_ROOT, "migrations")
    status = {}
    all_found = True
    for mig in EXPECTED_MIGRATIONS:
        path = os.path.join(migrations_dir, mig)
        exists = os.path.isfile(path) and os.path.getsize(path) > 0
        status[mig] = {
            "exists": exists,
            "size_bytes": os.path.getsize(path) if exists else 0,
        }
        if not exists:
            all_found = False
    return {
        "check": "migration_files",
        "passed": all_found,
        "directory": migrations_dir,
        "files": status,
    }

def verify_postgres():
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        return {
            "check": "postgres_runtime",
            "passed": False,
            "error": "psycopg2 is not installed",
        }

    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried_ports = []
    conn = None
    connected_port = None
    last_err = None

    for p in ports:
        if p in tried_ports:
            continue
        tried_ports.append(p)
        try:
            conn = psycopg2.connect(
                dbname="pol_test",
                user=os.environ.get("PGUSER", "postgres"),
                host=os.environ.get("PGHOST", "127.0.0.1"),
                port=p,
                connect_timeout=3,
            )
            connected_port = p
            break
        except Exception as e:
            last_err = str(e)
            continue

    if not conn:
        return {
            "check": "postgres_runtime",
            "passed": False,
            "ports_tried": tried_ports,
            "error": f"Could not connect to PostgreSQL 'pol_test': {last_err}",
        }

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT version();")
        pg_ver_full = cur.fetchone()["version"]
        is_pg18 = "PostgreSQL 18" in pg_ver_full

        cur.execute("""
            SELECT count(*) as cnt 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE';
        """)
        table_count = cur.fetchone()["cnt"]

        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
              AND table_type = 'BASE TABLE';
        """)
        existing_tables = set(r["table_name"] for r in cur.fetchall())
        missing_tables = [t for t in EXPECTED_CORE_TABLES if t not in existing_tables]

        cur.execute("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE event_object_table = 'organization_memberships'
              AND trigger_name = 'trg_enforce_org_membership_role_invariant';
        """)
        trigger_found = cur.fetchone() is not None

        conn.close()

        schema_valid = (table_count == EXPECTED_TABLE_COUNT) and (len(missing_tables) == 0) and trigger_found

        return {
            "check": "postgres_runtime",
            "passed": is_pg18 and schema_valid,
            "connected_port": connected_port,
            "pg_version_raw": pg_ver_full,
            "is_postgres_18": is_pg18,
            "table_count": table_count,
            "expected_table_count": EXPECTED_TABLE_COUNT,
            "missing_core_tables": missing_tables,
            "trigger_verified": trigger_found,
        }
    except Exception as e:
        conn.close()
        return {
            "check": "postgres_runtime",
            "passed": False,
            "connected_port": connected_port,
            "error": str(e),
        }

def run_environment_verification():
    checks = [
        verify_python(),
        verify_dependencies(),
        verify_migration_files(),
        verify_postgres(),
    ]

    all_passed = all(c.get("passed", False) for c in checks)
    return {
        "status": "PASS" if all_passed else "FAIL",
        "all_passed": all_passed,
        "checks": {c["check"]: c for c in checks},
    }

def main():
    parser = argparse.ArgumentParser(description="POL Environment & Bootstrap Verifier")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress human-readable progress")
    args = parser.parse_args()

    results = run_environment_verification()

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif not args.quiet:
        print("=" * 70)
        print("POL ENVIRONMENT & BOOTSTRAP VERIFICATION")
        print("=" * 70)
        for name, c in results["checks"].items():
            status = "PASS" if c.get("passed") else "FAIL"
            print(f"[{status}] {name}")
            for k, v in c.items():
                if k not in ["check", "passed"]:
                    print(f"      - {k}: {v}")
        print("=" * 70)
        print(f"OVERALL STATUS: {results['status']}")
        print("=" * 70)

    sys.exit(0 if results["all_passed"] else 1)

if __name__ == "__main__":
    main()
