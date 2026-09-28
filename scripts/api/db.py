"""PostgreSQL connection dependency for the production HTTP transport."""

from __future__ import annotations

import os
from collections.abc import Generator

import psycopg2
from psycopg2.extras import RealDictCursor


def get_runtime_connection():
    """Open one PostgreSQL connection for the current HTTP request.

    Production database identity is explicit through POL_API_DB_NAME/PGDATABASE;
    unlike the test migration helper, this function has no destructive behavior
    and no database fallback to a test database.
    """
    dbname = os.environ.get("POL_API_DB_NAME") or os.environ.get("PGDATABASE") or "pol"
    host = os.environ.get("POL_API_DB_HOST") or os.environ.get("PGHOST", "127.0.0.1")
    port = int(
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT", "5432")
    )
    user = os.environ.get("POL_API_DB_USER") or os.environ.get("PGUSER", "postgres")
    password = os.environ.get("POL_API_DB_PASSWORD") or os.environ.get("PGPASSWORD")
    sslmode = os.environ.get("POL_API_DB_SSLMODE", "prefer")
    environment = os.environ.get("ENVIRONMENT", "").lower()

    if environment in {"prod", "production"}:
        if not password:
            raise RuntimeError("Production PostgreSQL requires POL_API_DB_PASSWORD or PGPASSWORD.")
        if sslmode not in {"require", "verify-ca", "verify-full"}:
            raise RuntimeError(
                "Production PostgreSQL requires encrypted transport: "
                "set POL_API_DB_SSLMODE to require, verify-ca, or verify-full."
            )

    kwargs = {
        "dbname": dbname,
        "host": host,
        "port": port,
        "user": user,
        "connect_timeout": int(os.environ.get("POL_API_DB_CONNECT_TIMEOUT", "5")),
        "sslmode": sslmode,
    }
    if password:
        kwargs["password"] = password
    return psycopg2.connect(**kwargs)


def get_db_cursor() -> Generator:
    conn = get_runtime_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
