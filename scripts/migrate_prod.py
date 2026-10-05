"""Safe, forward-only PostgreSQL migration runner for VPS deployment.

Unlike scripts.migration_runner.py, this module never drops or resets a schema
and records the exact migration filename + SHA-256 before moving forward.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

from scripts.api.db import get_runtime_connection
from scripts.migration_runner import get_migration_chain

MARKER_TABLE = "pol_deployment_migrations"


def _migration_hash(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main() -> int:
    if os.getenv("ENVIRONMENT", "").lower() not in {"prod", "production"}:
        raise RuntimeError("Production migration runner requires ENVIRONMENT=production.")

    conn = get_runtime_connection()
    advisory_lock_held = False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS pol_deployment_migrations (
                    filename TEXT PRIMARY KEY,
                    sha256 CHAR(64) NOT NULL,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            conn.commit()

            cur.execute(
                """
                SELECT count(*)
                FROM information_schema.tables
                WHERE table_schema='public'
                  AND table_type='BASE TABLE'
                  AND table_name <> %s
                """,
                (MARKER_TABLE,),
            )
            existing_tables = int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM pol_deployment_migrations")
            recorded_count = int(cur.fetchone()[0])

            if recorded_count == 0 and existing_tables > 0:
                raise RuntimeError(
                    "Refusing to bootstrap a non-empty database without deployment migration history. "
                    "Use a fresh POL production database or reconcile it explicitly first."
                )

            cur.execute("SELECT pg_advisory_lock(hashtext('pol:deployment:migrations'))")
            advisory_lock_held = True
            conn.commit()

            recorded = {}
            cur.execute("SELECT filename, sha256 FROM pol_deployment_migrations")
            for row in cur.fetchall():
                recorded[row[0]] = row[1]

            migration_chain = get_migration_chain()

            for migration_path in migration_chain:
                filename = os.path.basename(migration_path)
                digest = _migration_hash(migration_path)

                if filename in recorded:
                    if recorded[filename] != digest:
                        raise RuntimeError(
                            f"Migration checksum changed after application: {filename}"
                        )
                    print(f"[MIGRATION] already applied: {filename}", flush=True)
                    continue

                print(f"[MIGRATION] applying: {filename}", flush=True)
                sql = Path(migration_path).read_text(encoding="utf-8")

                try:
                    cur.execute(sql)
                    cur.execute(
                        """
                        INSERT INTO pol_deployment_migrations(filename, sha256)
                        VALUES (%s, %s)
                        """,
                        (filename, digest),
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()
                    raise

                recorded[filename] = digest
                print(f"[MIGRATION] applied: {filename}", flush=True)

            cur.execute(
                """
                SELECT count(*)
                FROM information_schema.tables
                WHERE table_schema='public' AND table_type='BASE TABLE'
                """
            )
            table_count = int(cur.fetchone()[0])
            print(
                f"[MIGRATION] complete: {len(migration_chain)} migration files tracked; "
                f"{table_count} base tables present.",
                flush=True,
            )

    finally:
        if advisory_lock_held:
            try:
                conn.rollback()
                with conn.cursor() as cur:
                    cur.execute("SELECT pg_advisory_unlock(hashtext('pol:deployment:migrations'))")
                    conn.commit()
            except Exception:
                conn.rollback()
        conn.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
