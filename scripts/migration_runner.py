"""
POL Platform Canonical Migration Runner
Dynamically discovers and deterministically executes ordered SQL migrations
against PostgreSQL 18.
"""

import os
import glob
import psycopg2

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_MIGRATIONS_DIR = os.path.join(REPO_ROOT, "migrations")

def get_connection(dbname="pol_test"):
    """Connect to PostgreSQL with fallback for ports 5432 and 5433."""
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    last_err = None
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user="postgres",
                host="127.0.0.1",
                port=p
            )
            conn.autocommit = False
            return conn, p
        except Exception as e:
            last_err = e
    raise ConnectionError(f"Failed to connect to PostgreSQL db '{dbname}' on ports {tried}: {last_err}")

def get_migration_chain(migrations_dir=None):
    """
    Dynamically discover and return sorted list of SQL migration files.
    Ensures 001, 002, 003, ... are discovered in deterministic alphanumeric order.
    """
    mdir = migrations_dir or DEFAULT_MIGRATIONS_DIR
    if not os.path.isdir(mdir):
        raise FileNotFoundError(f"Migrations directory not found: {mdir}")
    
    pattern = os.path.join(mdir, "*.sql")
    files = glob.glob(pattern)
    files.sort(key=lambda p: os.path.basename(p))
    if not files:
        raise RuntimeError(f"No SQL migration files found in {mdir}")
    return files

def reset_schema(conn, dbname_expected="pol_test"):
    """
    Safely reset the public schema on the target test database.
    Strictly guards against resetting production or non-test databases.
    """
    dsn = conn.get_dsn_parameters()
    actual_db = dsn.get("dbname", "")
    if actual_db != dbname_expected:
        raise RuntimeError(
            f"DESTRUCTIVE RESET BLOCKED: Current database is '{actual_db}', expected '{dbname_expected}'!"
        )
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
    cur.execute("GRANT ALL ON SCHEMA public TO public;")
    conn.commit()

def apply_migration_chain(conn, migration_files=None, verbose=True):
    """
    Apply an ordered chain of SQL migration files within database transactions.
    """
    chain = migration_files if migration_files is not None else get_migration_chain()
    applied = []
    cur = conn.cursor()
    for mig_path in chain:
        rel_path = os.path.relpath(mig_path, REPO_ROOT)
        if verbose:
            print(f"[MIGRATION] Applying {rel_path}...")
        with open(mig_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        cur.execute(sql_content)
        conn.commit()
        applied.append(rel_path)
        if verbose:
            print(f"  [OK] Successfully applied {rel_path}")

    cur.execute("""
        SELECT count(*) 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE';
    """)
    table_count = cur.fetchone()[0]
    if verbose:
        print(f"[MIGRATION] Chain completed. Total active tables: {table_count}")
    return applied, table_count

if __name__ == "__main__":
    conn, port = get_connection("pol_test")
    print(f"Connected to PostgreSQL on port {port}")
    reset_schema(conn)
    applied, count = apply_migration_chain(conn)
    print(f"Applied {len(applied)} migrations: {applied}")
    conn.close()
