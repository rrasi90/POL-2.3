"""Fail-closed guards for destructive database operations (TODO-091)."""

from __future__ import annotations

import pytest

from scripts.db_safety import UnsafeDatabaseTarget, assert_isolated_test_target
from scripts.migration_runner import get_connection, reset_schema


class TestIsolatedTargetGuard:
    def test_allows_isolated_test_database_on_loopback(self):
        assert (
            assert_isolated_test_target(
                dbname="pol_test",
                host="127.0.0.1",
                environment="test",
                operation="unit",
            )
            == "pol_test"
        )

    def test_allows_localhost_alias(self):
        assert assert_isolated_test_target(
            dbname="pol_test", host="localhost", environment="test"
        ) == "pol_test"

    @pytest.mark.parametrize("dbname", ["pol", "pol_db", "pol_staging", "postgres"])
    def test_blocks_non_test_database_names(self, dbname):
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(
                dbname=dbname, host="127.0.0.1", environment="test", operation="wipe"
            )

    @pytest.mark.parametrize("environment", ["production", "prod", "staging", "LIVE"])
    def test_blocks_production_like_environments_even_for_test_db(self, environment):
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(
                dbname="pol_test", host="127.0.0.1", environment=environment
            )

    def test_blocks_remote_hosts(self):
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(
                dbname="pol_test", host="10.0.0.5", environment="test"
            )

    def test_blocks_missing_host(self):
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(
                dbname="pol_test", host="", environment="test"
            )

    def test_maintenance_database_requires_explicit_opt_in(self):
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(
                dbname="postgres", host="127.0.0.1", environment="test"
            )
        assert (
            assert_isolated_test_target(
                dbname="postgres",
                host="127.0.0.1",
                environment="test",
                allow_maintenance=True,
            )
            == "postgres"
        )

    def test_maintenance_database_still_requires_loopback(self):
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(
                dbname="postgres",
                host="10.0.0.5",
                environment="test",
                allow_maintenance=True,
            )

    def test_reads_target_from_environment(self, monkeypatch):
        monkeypatch.setenv("POL_API_DB_NAME", "pol_test")
        monkeypatch.setenv("POL_API_DB_HOST", "127.0.0.1")
        monkeypatch.setenv("ENVIRONMENT", "test")
        assert assert_isolated_test_target() == "pol_test"

        monkeypatch.setenv("POL_API_DB_NAME", "pol")
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target()

    def test_blocks_when_no_database_is_resolvable(self, monkeypatch):
        for name in ("POL_API_DB_NAME", "PGDATABASE"):
            monkeypatch.delenv(name, raising=False)
        with pytest.raises(UnsafeDatabaseTarget):
            assert_isolated_test_target(dbname="", host="127.0.0.1", environment="test")


class TestSchemaResetGuard:
    def test_reset_refuses_foreign_database_name(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "test")
        conn, _ = get_connection("pol_test")
        try:
            with pytest.raises(RuntimeError):
                reset_schema(conn, dbname_expected="pol")
        finally:
            conn.close()

    def test_reset_refuses_production_environment(self, monkeypatch):
        conn, _ = get_connection("pol_test")
        try:
            monkeypatch.setenv("ENVIRONMENT", "production")
            with pytest.raises(UnsafeDatabaseTarget):
                reset_schema(conn, dbname_expected="pol_test")
        finally:
            conn.close()
