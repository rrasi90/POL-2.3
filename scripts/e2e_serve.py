"""Browser E2E backend launcher: migrate → seed → serve (TODO-006).

Used by `mvp/apps/web/playwright.config.ts` as the first webServer. Keeps the
whole stack reproducible from a single command so local runs and CI share one
code path:

    python scripts/e2e_serve.py             # migrate + seed + serve
    python scripts/e2e_serve.py --prepare   # migrate + seed only (no server)
    python scripts/e2e_serve.py --reset     # drop public schema, re-apply chain

Environment defaults below are test-only values; production never runs this
module (PRODUCTION_DB_PASSWORD / PROD guards live elsewhere).
"""

from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_API_PORT = 8001
TEST_JWT_SECRET = "test-secret-key-for-auth-contract-tests-only-32bytes!!"
DEFAULT_FIXTURE = os.path.join(REPO_ROOT, "mvp", "apps", "web", "tests", ".e2e-fixture.json")


def _apply_env_defaults() -> int:
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("POL_ENV", "test")
    os.environ.setdefault("POL_JWT_SECRET", TEST_JWT_SECRET)
    os.environ.setdefault("POL_API_DB_NAME", "pol_test")
    os.environ.setdefault("PGDATABASE", "pol_test")
    os.environ.setdefault("PGHOST", "127.0.0.1")
    os.environ.setdefault("POL_API_DB_HOST", os.environ["PGHOST"])
    port = os.environ.get("POL_API_DB_PORT") or os.environ.get("PGPORT") or "5432"
    os.environ.setdefault("POL_API_DB_PORT", port)
    os.environ.setdefault("PGPORT", port)
    return int(port)


def prepare(reset: bool = False) -> None:
    from scripts.e2e_seed import seed
    from scripts.migration_runner import (
        apply_migration_chain,
        get_connection,
        reset_schema,
    )

    conn, port = get_connection(os.environ.get("POL_API_DB_NAME", "pol_test"))
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT to_regclass('public.baskets') IS NOT NULL "
                "AND to_regclass('public.user_sessions') IS NOT NULL;"
            )
            schema_ready = bool(cur.fetchone()[0])
        if reset:
            reset_schema(conn)
            schema_ready = False
        if schema_ready:
            print("[E2E] schema already migrated, skipping chain", flush=True)
            applied, tables = [], 0
        else:
            applied, tables = apply_migration_chain(conn, verbose=False)
    finally:
        conn.close()
    print(f"[E2E] migrations={len(applied)} tables={tables} port={port}", flush=True)
    fixture = seed()
    fixture_path = os.environ.get("POL_E2E_FIXTURE", DEFAULT_FIXTURE)
    os.makedirs(os.path.dirname(fixture_path), exist_ok=True)
    with open(fixture_path, "w", encoding="utf-8") as fh:
        json.dump(fixture, fh, ensure_ascii=True, indent=2)
    print(
        f"[E2E] seeded retailers={len(fixture['retailer_phones'])} "
        f"products={len(fixture['products'])} "
        f"closed_baskets={fixture['closed_baskets']} "
        f"fixture={fixture_path}",
        flush=True,
    )


def main() -> int:
    port = _apply_env_defaults()
    prepare(reset="--reset" in sys.argv)
    if "--prepare" in sys.argv:
        return 0

    import uvicorn

    api_port = int(os.environ.get("POL_E2E_API_PORT", DEFAULT_API_PORT))
    host = os.environ.get("POL_E2E_API_HOST", "127.0.0.1")
    print(f"[E2E] serving API on http://{host}:{api_port} (pg {port})", flush=True)
    uvicorn.run(
        "scripts.api.main:app",
        host=host,
        port=api_port,
        log_level="warning",
        access_log=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
