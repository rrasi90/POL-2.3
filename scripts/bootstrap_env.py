# -*- coding: utf-8 -*-
"""
POL Environment Bootstrap & Safety Harness
Validates dependencies, database connection, and executes migration chain safely.
"""

import os
import sys
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def ensure_dependencies():
    print("[BOOTSTRAP] Checking Python dependencies...")
    try:
        import psycopg2
        print("  [OK] psycopg2 is installed.")
    except ImportError:
        print("  [WARN] psycopg2 not found. Installing psycopg2-binary from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary>=2.9.9"])
        import psycopg2
        print("  [OK] psycopg2-binary installed successfully.")

def get_connection(dbname="pol_test"):
    import psycopg2
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            conn = psycopg2.connect(dbname=dbname, user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn, p
        except Exception:
            continue
    raise ConnectionError(f"Could not connect to PostgreSQL on ports {tried} with dbname={dbname}")

def run_migrations_safely(reset=False):
    import psycopg2
    ensure_dependencies()

    if reset:
        # Strict destructive reset safety guard
        allow_reset = os.environ.get("POL_ALLOW_TEST_DB_RESET", "0") == "1"
        conn, port = get_connection("pol_test")
        dsn_params = conn.get_dsn_parameters()
        actual_db = dsn_params.get("dbname", "")
        
        if actual_db != "pol_test":
            conn.close()
            raise RuntimeError(f"FATAL: Destructive reset attempted on non-test database: '{actual_db}'! Only 'pol_test' is permitted.")
        
        if not allow_reset:
            conn.close()
            raise RuntimeError("FATAL: Destructive reset requires environment variable POL_ALLOW_TEST_DB_RESET=1.")

        print(f"[BOOTSTRAP] Resetting public schema on '{actual_db}' (port {port})...")
        cur = conn.cursor()
        cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;")
        conn.commit()
    else:
        conn, port = get_connection("pol_test")
        cur = conn.cursor()

    # Migration Chain Execution
    migration_chain = [
        os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql"),
        os.path.join(REPO_ROOT, "migrations", "002_platform_core_schema.sql")
    ]

    for mig in migration_chain:
        rel_mig = os.path.relpath(mig, REPO_ROOT)
        if not os.path.exists(mig):
            raise FileNotFoundError(f"Migration file missing: {mig}")
        print(f"[BOOTSTRAP] Applying {rel_mig}...")
        with open(mig, "r", encoding="utf-8") as f:
            ddl = f.read()
        cur.execute(ddl)
        conn.commit()
        print(f"  [OK] Applied {rel_mig}.")

    cur.execute("""
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE';
    """)
    table_count = cur.fetchone()[0]
    print(f"[BOOTSTRAP] Successfully migrated PostgreSQL 18. Total active tables: {table_count}")
    conn.close()
    return table_count

if __name__ == "__main__":
    do_reset = "--reset" in sys.argv
    if do_reset:
        os.environ["POL_ALLOW_TEST_DB_RESET"] = "1"
    run_migrations_safely(reset=do_reset)
