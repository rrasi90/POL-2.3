"""Canonical notification inbox retention worker."""

from __future__ import annotations

from datetime import datetime, timezone


def archive_expired_inbox_items(cur, *, now: datetime | None = None, batch_size: int = 500) -> int:
    """Archive expired inbox items with row-level locking suitable for parallel workers."""
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    effective_now = now or datetime.now(timezone.utc)

    cur.execute(
        """
        WITH expired AS (
            SELECT id
            FROM user_inbox_items
            WHERE is_archived = FALSE
              AND expires_at IS NOT NULL
              AND expires_at <= %s
            ORDER BY expires_at ASC, id ASC
            FOR UPDATE SKIP LOCKED
            LIMIT %s
        )
        UPDATE user_inbox_items ui
        SET is_archived = TRUE
        FROM expired
        WHERE ui.id = expired.id
          AND ui.is_archived = FALSE
        RETURNING ui.id;
        """,
        (effective_now, batch_size),
    )
    return len(cur.fetchall())
