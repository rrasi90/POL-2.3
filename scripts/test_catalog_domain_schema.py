"""Static verification of catalog domain schema invariants — Stage 13.

Validates that all catalog tables exist, key columns are present,
and critical constraints/indexes are enforced. No external dependencies
beyond a live PG connection (runs against pol_test).
"""

from __future__ import annotations

import os

import psycopg2
import pytest


def _conn():
    port = int(
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT", "5432")
    )
    return psycopg2.connect(
        dbname="pol_test",
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=port,
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
    )


CATALOG_TABLES = [
    "brands",
    "categories",
    "subcategories",
    "products",
    "product_reference_metadata",
    "product_identifiers",
    "media_assets",
    "product_media",
    "product_candidates",
    "product_merge_history",
    "vendor_products",
    "vendor_inventory",
    "vendor_prices",
    "inventory_audit_log",
    "daily_inventory_confirmations",
    "daily_inventory_confirmation_items",
    "vendor_inventory_responsibilities",
]


def test_all_catalog_tables_exist():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
            existing = {row[0] for row in cur.fetchall()}
            for table in CATALOG_TABLES:
                assert table in existing, f"Missing catalog table: {table}"
    finally:
        conn.close()


def test_products_has_master_sku_unique():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT constraint_name FROM information_schema.table_constraints "
                "WHERE table_name = 'products' AND constraint_type = 'UNIQUE'"
            )
            unique_constraints = {row[0] for row in cur.fetchall()}
            assert any("master_sku" in c for c in unique_constraints), (
                "products.master_sku must have a UNIQUE constraint"
            )
    finally:
        conn.close()


def test_vendor_products_has_sku_uniqueness():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT constraint_name FROM information_schema.table_constraints "
                "WHERE table_name = 'vendor_products' AND constraint_type = 'UNIQUE'"
            )
            unique_constraints = {row[0] for row in cur.fetchall()}
            assert any("vendor_product_sku" in c for c in unique_constraints), (
                "vendor_products must have a (vendor_id, vendor_sku) UNIQUE constraint"
            )
    finally:
        conn.close()


def test_vendor_inventory_has_moq_column():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'vendor_inventory' AND column_name = 'moq'"
            )
            assert cur.fetchone() is not None, "vendor_inventory.moq column must exist"
    finally:
        conn.close()


def test_vendor_prices_has_temporal_exclusion():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT conname FROM pg_constraint "
                "WHERE conrelid = 'vendor_prices'::regclass "
                "AND contype = 'x'"
            )
            row = cur.fetchone()
            assert row is not None, (
                "vendor_prices must have a GiST exclusion constraint"
            )
            assert "overlap" in row[0] or "vendor_price" in row[0]
    finally:
        conn.close()


def test_product_identifiers_has_multi_scope_indexes():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT indexname FROM pg_indexes "
                "WHERE tablename = 'product_identifiers'"
            )
            indexes = {row[0] for row in cur.fetchall()}
            assert any("lookup" in i for i in indexes), (
                "product_identifiers must have an identifier_value lookup index"
            )
    finally:
        conn.close()


def test_product_candidates_has_status_check():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                "WHERE conrelid = 'product_candidates'::regclass "
                "AND contype = 'c'"
            )
            check_defs = [row[0] for row in cur.fetchall()]
            status_checks = [c for c in check_defs if "PENDING_REVIEW" in c or "APPROVED_CANONICAL" in c]
            assert status_checks, "product_candidates must have a status CHECK constraint"
    finally:
        conn.close()


def test_vendor_inventory_has_reserved_le_physical_check():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                "WHERE conrelid = 'vendor_inventory'::regclass "
                "AND contype = 'c'"
            )
            check_defs = [row[0] for row in cur.fetchall()]
            reserved_checks = [c for c in check_defs if "reserved" in c.lower() and "physical" in c.lower()]
            assert reserved_checks, "vendor_inventory must have reserved <= physical CHECK"
    finally:
        conn.close()


def test_inventory_audit_log_has_source_trigger_column():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT column_name, is_nullable FROM information_schema.columns "
                "WHERE table_name = 'inventory_audit_log' AND column_name = 'source_trigger'"
            )
            row = cur.fetchone()
            assert row is not None, "inventory_audit_log.source_trigger column must exist"
            assert row[1] == "NO", "source_trigger must be NOT NULL"
    finally:
        conn.close()
