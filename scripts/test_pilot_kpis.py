"""Tests for Pilot KPI Measurement Pipeline — Stage 37."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.pilot_kpis import KPI_QUERIES, compute_all_kpis, compute_kpi, weekly_snapshot


def _db():
    port = int(os.environ.get("POL_API_DB_PORT") or os.environ.get("PGPORT", "5432"))
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=port,
        user=os.environ.get("PGUSER", "postgres"),
    )


def _seed_orders(cur, count=5, days_ago=1):
    """Seed test orders with fixture data."""
    retailer_user_id = str(uuid4())
    vendor_user_id = str(uuid4())
    created = datetime.now(timezone.utc) - timedelta(days=days_ago)
    cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'R', 'RETAILER_OWNER')",
                (retailer_user_id, f"+9893{uuid4().hex[:8]}"))
    cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'V', 'VENDOR_OWNER')",
                (vendor_user_id, f"+9890{uuid4().hex[:8]}"))
    retailer_id = str(uuid4())
    vendor_id = str(uuid4())
    cur.execute("INSERT INTO retailers (id, user_id, store_name, city, neighborhood, address, onboarding_status) VALUES (%s, %s, 'Test Store', 'Tehran', 'Central', '123 Main', 'REGISTERED')",
                (retailer_id, retailer_user_id))
    cur.execute("INSERT INTO vendors (id, user_id, business_name, cluster_location, warehouse_address, min_order_value_toman, status) VALUES (%s, %s, 'Test Vendor', 'Tehran', '456 Warehouse Rd', 50000, 'ACTIVE')",
                (vendor_id, vendor_user_id))
    og_id = str(uuid4())
    cur.execute(
        "INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, order_count) "
        "VALUES (%s, %s, 'COMPLETED', %s, %s)",
        (og_id, retailer_id, 100000 * count, count),
    )
    order_ids = []
    for i in range(count):
        oid = str(uuid4())
        order_number = f"ORD-TEST-{oid[:8].upper()}"
        cur.execute(
            "INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, total_amount_toman, order_status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, 'DELIVERED', %s)",
            (oid, order_number, og_id, retailer_id, vendor_id, 100000 * (i + 1), created),
        )
        order_ids.append(oid)
    return retailer_id, vendor_id, order_ids, created


class TestKPIDefinitions:
    def test_all_ten_kpis_defined(self):
        assert len(KPI_QUERIES) == 10

    def test_each_kpi_has_sql(self):
        for name, kpi in KPI_QUERIES.items():
            assert "sql" in kpi, f"{name} missing sql"
            assert "description" in kpi, f"{name} missing description"
            assert "params" in kpi, f"{name} missing params"


class TestKPIComputation:
    def test_gmv_computes(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                _seed_orders(cur, 3, 1)
            conn.commit()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()
                result = compute_kpi(cur, "gmv", today - timedelta(days=7), today + timedelta(days=1))
                assert result["name"] == "gmv"
                assert result["value"] >= 0
                assert result["description"] == "Gross Merchandise Value"
        finally:
            conn.close()

    def test_aov_computes(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                _seed_orders(cur, 2, 1)
            conn.commit()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()
                result = compute_kpi(cur, "aov", today - timedelta(days=7), today + timedelta(days=1))
                assert result["name"] == "aov"
                assert result["value"] >= 0
        finally:
            conn.close()

    def test_unknown_kpi_raises(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                with pytest.raises(ValueError, match="Unknown KPI"):
                    compute_kpi(cur, "nonexistent", date.today(), date.today())
        finally:
            conn.close()

    def test_empty_date_range_returns_zero(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                result = compute_kpi(cur, "gmv", date(2000, 1, 1), date(2000, 1, 2))
                assert result["value"] == 0.0
        finally:
            conn.close()


class TestComputeAllKPIs:
    def test_returns_ten_results(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()
                results = compute_all_kpis(cur, today - timedelta(days=7), today + timedelta(days=1))
                assert len(results) == 10
                names = [r["name"] for r in results]
                assert "gmv" in names
                assert "aov" in names
                assert "repeat_rate" in names
        finally:
            conn.close()

    def test_all_results_have_expected_shape(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()
                results = compute_all_kpis(cur, today - timedelta(days=7), today + timedelta(days=1))
                for r in results:
                    assert "name" in r
                    assert "description" in r
                    assert "value" in r
                    assert "start_date" in r
                    assert "end_date" in r
                    assert isinstance(r["value"], float)
        finally:
            conn.close()


class TestWeeklySnapshot:
    def test_snapshot_returns_expected_keys(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()
                snap = weekly_snapshot(cur, today)
                assert "snapshot_date" in snap
                assert "week_start" in snap
                assert "kpis" in snap
                assert len(snap["kpis"]) == 10
        finally:
            conn.close()

    def test_snapshot_date_range_is_seven_days(self):
        conn = _db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                today = date.today()
                snap = weekly_snapshot(cur, today)
                start = date.fromisoformat(snap["week_start"])
                end = date.fromisoformat(snap["snapshot_date"])
                assert (end - start).days == 6
        finally:
            conn.close()
