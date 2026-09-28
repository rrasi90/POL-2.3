"""One-shot notification retention maintenance entry point.

The deployment scheduler should invoke this script at least daily.
It intentionally performs only the canonical expiry/archive operation.
"""

from __future__ import annotations

import os
import psycopg2

from scripts.notification_retention_worker import archive_expired_inbox_items


def main() -> int:
    dsn = os.getenv("POL_PG_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("POL_PG_DSN or DATABASE_URL is required.")

    batch_size = int(os.getenv("NOTIFICATION_RETENTION_BATCH_SIZE", "500"))
    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            archived = archive_expired_inbox_items(cur, batch_size=batch_size)
        conn.commit()

    print(f"notification-retention archived={archived}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
