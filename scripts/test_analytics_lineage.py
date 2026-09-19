"""Tests for Analytics Event Lineage — Stage 36."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.analytics_lineage import KPI_DEFINITIONS, REQUIRED_TABLES, validate_lineage


def _cur():
    port = int(os.environ.get("POL_API_DB_PORT") or os.environ.get("PGPORT", "5432"))
    conn = psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=port,
        user=os.environ.get("PGUSER", "postgres"),
    )
    return conn, conn.cursor(cursor_factory=RealDictCursor)


class TestKPIDefinitions:
    def test_all_ten_kpis_defined(self):
        assert len(KPI_DEFINITIONS) == 10

    def test_each_kpi_has_required_fields(self):
        for name, kpi in KPI_DEFINITIONS.items():
            assert "description" in kpi, f"{name} missing description"
            assert "source_table" in kpi, f"{name} missing source_table"
            assert "source_event" in kpi, f"{name} missing source_event"
            assert "calculation" in kpi, f"{name} missing calculation"
            assert "timezone" in kpi, f"{name} missing timezone"

    def test_all_timezones_are_tehran(self):
        for name, kpi in KPI_DEFINITIONS.items():
            assert kpi["timezone"] == "Asia/Tehran", f"{name} has wrong timezone"


class TestSourceTablesExist:
    def test_source_tables_exist_in_db(self):
        conn, cur = _cur()
        try:
            missing = validate_lineage(cur)
            assert missing == [], f"Missing tables: {missing}"
        finally:
            conn.close()
