"""Fail-closed guard for destructive database operations in tests and tooling.

A QA credential must never be able to wipe or mutate the primary database. Every
destructive operation (schema reset, truncate, bulk delete, load/fault
injection) resolves its target through this module first.
"""

from __future__ import annotations

import os

LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1", ""})
ISOLATED_DB_SUFFIX = "_test"
MAINTENANCE_DBS = frozenset({"postgres", "template1"})
PRODUCTION_ENVIRONMENTS = frozenset({"prod", "production", "staging", "live"})


class UnsafeDatabaseTarget(RuntimeError):
    """Raised when a destructive operation points at a non-isolated target."""


def resolve_target(dbname: str | None = None, host: str | None = None) -> tuple[str, str]:
    resolved_db = (
        dbname
        or os.environ.get("POL_API_DB_NAME")
        or os.environ.get("PGDATABASE")
        or ""
    ).strip()
    resolved_host = (
        host
        or os.environ.get("POL_API_DB_HOST")
        or os.environ.get("PGHOST")
        or ""
    ).strip().lower()
    return resolved_db, resolved_host


def assert_isolated_test_target(
    dbname: str | None = None,
    host: str | None = None,
    *,
    environment: str | None = None,
    operation: str = "destructive database operation",
    allow_maintenance: bool = False,
) -> str:
    """Return the verified database name or raise `UnsafeDatabaseTarget`.

    Allowed: `*_test` databases on a loopback host, in a non-production
    environment. Maintenance databases (postgres/template1) require an explicit
    `allow_maintenance=True` and are used only for cluster-level tasks such as
    creating an isolated test database.
    """

    resolved_db, resolved_host = resolve_target(dbname, host)
    resolved_env = (
        environment if environment is not None else os.environ.get("ENVIRONMENT", "")
    ).strip().lower()
    pol_env = os.environ.get("POL_ENV", "").strip().lower()

    if resolved_env in PRODUCTION_ENVIRONMENTS or pol_env in PRODUCTION_ENVIRONMENTS:
        raise UnsafeDatabaseTarget(
            f"BLOCKED {operation}: production-like environment "
            f"(ENVIRONMENT={resolved_env or '-'}, POL_ENV={pol_env or '-'})."
        )

    if not resolved_db:
        raise UnsafeDatabaseTarget(
            f"BLOCKED {operation}: no database name resolved (set POL_API_DB_NAME)."
        )

    if allow_maintenance and resolved_db in MAINTENANCE_DBS:
        return resolved_db

    if not resolved_db.endswith(ISOLATED_DB_SUFFIX):
        raise UnsafeDatabaseTarget(
            f"BLOCKED {operation}: '{resolved_db}' is not an isolated test database "
            f"(expected a '*{ISOLATED_DB_SUFFIX}' name)."
        )

    if resolved_host not in LOOPBACK_HOSTS:
        raise UnsafeDatabaseTarget(
            f"BLOCKED {operation}: host '{resolved_host}' is not loopback."
        )

    return resolved_db
