import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def setup_db():
    conn = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', port=5433)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("DROP DATABASE IF EXISTS pol_test;")
    cur.execute("CREATE DATABASE pol_test;")
    conn.close()

    conn_test = psycopg2.connect(dbname='pol_test', user='postgres', host='127.0.0.1', port=5433)
    cur_test = conn_test.cursor()
    schema_file = os.path.join(REPO_ROOT, "migrations", "001_initial_schema.sql")
    with open(schema_file, "r", encoding="utf-8") as f:
        ddl = f.read()

    cur_test.execute(ddl)
    conn_test.commit()

    cur_test.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur_test.fetchall()]
    print(f"SUCCESSFULLY APPLIED 001_initial_schema.sql! Created {len(tables)} tables:")
    for t in tables:
        print(f"  - {t}")
    conn_test.close()

if __name__ == "__main__":
    setup_db()
