"""Reconcile DB media DELETED state with object storage."""

from __future__ import annotations

from datetime import datetime, timezone


class MediaStorageReconcileError(RuntimeError):
    pass


def reconcile_deleted_media(cur, *, s3_client_factory, batch_size: int = 100, now: datetime | None = None) -> dict:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    now = now or datetime.now(timezone.utc)

    cur.execute(
        """
        SELECT id, storage_bucket, storage_key
        FROM media_assets
        WHERE status='DELETED'
          AND storage_deleted_at IS NULL
        ORDER BY created_at, id
        FOR UPDATE SKIP LOCKED
        LIMIT %s
        """,
        (batch_size,),
    )
    assets = cur.fetchall()
    reconciled = 0
    failures = 0

    for asset in assets:
        try:
            s3 = s3_client_factory()
            s3.delete_object(Bucket=asset["storage_bucket"], Key=asset["storage_key"])

            cur.execute(
                """
                UPDATE media_variants
                SET storage_delete_attempts = storage_delete_attempts + 1,
                    storage_deleted_at = now(),
                    storage_delete_error = NULL
                WHERE source_media_asset_id=%s
                  AND storage_deleted_at IS NULL
                """,
                (asset["id"],),
            )
            cur.execute(
                """
                UPDATE media_assets
                SET storage_delete_attempts = storage_delete_attempts + 1,
                    storage_deleted_at = now(),
                    storage_delete_error = NULL
                WHERE id=%s
                """,
                (asset["id"],),
            )
            # Delete variant objects after the source object; DB metadata remains
            # as durable provenance/audit, with storage_deleted_at marking success.
            cur.execute(
                """
                SELECT id, storage_bucket, storage_key
                FROM media_variants
                WHERE source_media_asset_id=%s
                  AND storage_deleted_at IS NOT NULL
                """,
                (asset["id"],),
            )
            variants = cur.fetchall()
            for variant in variants:
                s3.delete_object(Bucket=variant["storage_bucket"], Key=variant["storage_key"])
            reconciled += 1
        except Exception as exc:
            failures += 1
            cur.execute(
                """
                UPDATE media_assets
                SET storage_delete_attempts = storage_delete_attempts + 1,
                    storage_delete_error = %s
                WHERE id=%s
                """,
                (str(exc)[:2000], asset["id"]),
            )

    return {"scanned": len(assets), "reconciled": reconciled, "failures": failures}
