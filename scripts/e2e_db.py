"""JSON facade over PostgreSQL for browser E2E assertions (TODO-006).

Playwright has no Postgres driver, so tests shell out to this module to assert
server-side truth (basket count, item rows) instead of trusting the client.

    python scripts/e2e_db.py baskets +989123456000
    python scripts/e2e_db.py counts  +989123456000

Output is ASCII-only JSON (ensure_ascii) so Windows consoles can read it.
"""

from __future__ import annotations

import json
import os
import sys

import psycopg2
from psycopg2.extras import RealDictCursor

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def _connect():
    port = int(
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT")
        or "5432"
    )
    return psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST") or os.environ.get("PGHOST", "127.0.0.1"),
        port=port,
        user=os.environ.get("POL_API_DB_USER") or os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("POL_API_DB_PASSWORD") or os.environ.get("PGPASSWORD"),
        connect_timeout=5,
    )


def _retailer_id(cur, phone: str):
    cur.execute(
        """
        SELECT r.id
        FROM retailers r
        JOIN users u ON u.id = r.user_id
        WHERE u.phone_number = %s
        LIMIT 1;
        """,
        (phone,),
    )
    row = cur.fetchone()
    if not row:
        raise SystemExit(f"no retailer for phone {phone}")
    return row["id"]


def baskets(phone: str) -> list[dict]:
    conn = _connect()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            retailer_id = _retailer_id(cur, phone)
            cur.execute(
                """
                SELECT b.id, b.status, b.version,
                       to_char(b.created_at, 'YYYY-MM-DD"T"HH24:MI:SS.MSZ') AS created_at
                  FROM baskets b
                 WHERE b.retailer_id = %s
                 ORDER BY b.created_at ASC, b.id ASC;
                """,
                (retailer_id,),
            )
            rows = [dict(r) for r in cur.fetchall()]
            for row in rows:
                cur.execute(
                    """
                    SELECT bi.product_id, bi.requested_quantity, bi.pack_quantity,
                           bi.requested_unit
                      FROM basket_items bi
                     WHERE bi.basket_id = %s
                     ORDER BY bi.created_at ASC, bi.id ASC;
                    """,
                    (row["id"],),
                )
                row["items"] = [dict(i) for i in cur.fetchall()]
            return rows
    finally:
        conn.close()


def counts(phone: str) -> dict:
    rows = baskets(phone)
    return {
        "total": len(rows),
        "open": sum(1 for r in rows if r["status"] == "OPEN"),
        "statuses": [r["status"] for r in rows],
    }


def reset(phone: str) -> dict:
    """Drop every basket of the tenant so a (re)run starts from zero."""
    conn = _connect()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            retailer_id = _retailer_id(cur, phone)
            cur.execute("DELETE FROM baskets WHERE retailer_id = %s;", (retailer_id,))
            deleted = cur.rowcount
            cur.execute(
                "DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,)
            )
            otp_deleted = cur.rowcount
        conn.commit()
        return {"deleted_baskets": deleted, "deleted_otp_challenges": otp_deleted}
    finally:
        conn.close()


COMMANDS = {"baskets": baskets, "counts": counts, "reset": reset}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in COMMANDS:
        print(f"usage: python {os.path.basename(__file__)} <{'|'.join(COMMANDS)}> <phone>")
        return 2
    result = COMMANDS[argv[0]](argv[1])
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
