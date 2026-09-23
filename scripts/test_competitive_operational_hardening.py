#!/usr/bin/env python3
"""Regression tests for migration 005 and evidence-derived operational policies."""

import os
import sys
import uuid
import datetime
import pytest
from psycopg2.extras import RealDictCursor

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.migration_runner import get_connection
from scripts.operational_policies import PaymentReconciliationPolicy


@pytest.fixture
def db():
    conn, port = get_connection("pol_test")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    yield conn, cur
    conn.rollback()
    conn.close()


def test_operational_hardening_tables_exist(db):
    conn, cur = db
    expected = {
        "vendor_operating_windows",
        "vendor_capacity_profiles",
        "retailer_locations",
        "commercial_terms",
        "payment_evidence",
        "payment_reconciliation_cases",
        "retailer_saved_lists",
        "retailer_saved_list_items",
        "data_consents",
        "risk_events",
        "metric_definitions",
        "experiments",
        "experiment_assignments",
    }
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
          AND table_name = ANY(%s);
        """,
        (list(expected),),
    )
    found = {r["table_name"] for r in cur.fetchall()}
    assert found == expected


def test_checkout_idempotency_constraint_exists(db):
    conn, cur = db
    cur.execute(
        """
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND indexname = 'uq_order_groups_checkout_idempotency_key';
        """
    )
    assert cur.fetchone() is not None


def test_inventory_reserved_quantity_is_constrained(db):
    conn, cur = db
    cur.execute(
        """
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'chk_vendor_inventory_reserved_le_physical';
        """
    )
    assert cur.fetchone() is not None


def test_payment_reconciliation_policy():
    assert PaymentReconciliationPolicy.status_for(1000, None) == "OPEN"
    assert PaymentReconciliationPolicy.status_for(1000, 1000) == "MATCHED"
    assert PaymentReconciliationPolicy.status_for(1000, 500) == "PARTIALLY_MATCHED"
    assert PaymentReconciliationPolicy.status_for(1000, 0) == "MISMATCH"
    assert PaymentReconciliationPolicy.status_for(1000, 1200) == "MISMATCH"


def test_effective_price_overlap_constraint_exists(db):
    conn, cur = db
    cur.execute(
        """
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ex_vendor_price_no_overlap';
        """
    )
    assert cur.fetchone() is not None


def test_metric_lineage_requires_calculation_version(db):
    conn, cur = db
    cur.execute("SELECT calculation_version, timezone FROM metric_definitions LIMIT 1;")
    # Empty by default is valid; the schema itself must expose both fields.
    cols = []
    cur.execute(
        """
        SELECT column_name FROM information_schema.columns
        WHERE table_schema='public' AND table_name='metric_definitions'
          AND column_name IN ('calculation_version','timezone','source_events','source_tables');
        """
    )
    cols = {r["column_name"] for r in cur.fetchall()}
    assert cols == {"calculation_version", "timezone", "source_events", "source_tables"}
