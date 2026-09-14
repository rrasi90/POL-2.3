import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.migration_runner import get_connection, apply_migration_chain

def setup_db():
    # Try connecting to postgres DB to recreate pol_test
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    pg_conn = None
    connected_port = None
    for p in ports:
        try:
            pg_conn = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', port=p)
            connected_port = p
            break
        except Exception:
            continue

    if pg_conn:
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = pg_conn.cursor()
        cur.execute("DROP DATABASE IF EXISTS pol_test;")
        cur.execute("CREATE DATABASE pol_test;")
        pg_conn.close()
        print(f"[SETUP] Recreated database 'pol_test' on port {connected_port}.")

    conn_test, port = get_connection("pol_test")
    applied, table_count = apply_migration_chain(conn_test, verbose=True)

    cur_test = conn_test.cursor()
    cur_test.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur_test.fetchall()]
    print(f"SUCCESSFULLY APPLIED MIGRATIONS! Total tables: {len(tables)} ({table_count})")
    for t in tables:
        print(f"  - {t}")
    conn_test.close()

if __name__ == "__main__":
    setup_db()
