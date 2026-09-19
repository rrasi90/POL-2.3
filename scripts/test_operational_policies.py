"""Unit tests for operational_policies.py — Stage 19 contract reconciliation.

Tests validate_allocation_against_basket: the pre-transactional guard
that rejects forged/stale allocation input before checkout.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from psycopg2.extras import RealDictCursor

from scripts.migration_runner import get_connection
from scripts.operational_policies import (
    AllocationIntegrityError,
    validate_allocation_against_basket,
)


def _db():
    conn, _ = get_connection("pol_test")
    return conn


def _seed_basket_and_plan(cur, suffix, *, basket_status="OPEN", plan_status="CONFIRMED",
                          version=1, plan_version=1, expires_in_minutes=15):
    retailer_user = str(uuid4())
    retailer_org = str(uuid4())
    retailer_id = str(uuid4())
    vendor_user = str(uuid4())
    vendor_org = str(uuid4())
    vendor_id = str(uuid4())
    brand_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    product_id = str(uuid4())
    vendor_product_id = str(uuid4())
    basket_id = str(uuid4())
    plan_id = str(uuid4())
    allocation_item_id = str(uuid4())

    cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Retailer', 'RETAILER_OWNER')",
                (retailer_user, f"+9891{uuid4().int % 100000000:08d}"))
    cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Retailer Org', 'RETAILER', 'ACTIVE')",
                (retailer_org,))
    cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')",
                (str(uuid4()), retailer_org, retailer_user))
    cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES (%s, %s, %s, 'Store', 'Ahvaz', 'Naderi', 'Test')",
                (retailer_id, retailer_user, retailer_org))

    cur.execute("INSERT INTO users (id, phone_number, full_name, role) VALUES (%s, %s, 'Vendor', 'VENDOR_OWNER')",
                (vendor_user, f"+9891{uuid4().int % 100000000:08d}"))
    cur.execute("INSERT INTO organizations (id, name, org_type, status) VALUES (%s, 'Vendor Org', 'VENDOR', 'ACTIVE')",
                (vendor_org,))
    cur.execute("INSERT INTO organization_memberships (id, organization_id, user_id, role, status) VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')",
                (str(uuid4()), vendor_org, vendor_user))
    cur.execute("INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman, status) "
                "VALUES (%s, %s, %s, 'Vendor', 'Ahvaz', 1000000, 'ACTIVE')",
                (vendor_id, vendor_user, vendor_org))

    cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, %s, %s)", (brand_id, f"B{suffix}", f"b-{suffix}"))
    cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, %s, %s)", (category_id, f"C{suffix}", f"c-{suffix}"))
    cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, %s, %s)",
                (subcategory_id, category_id, f"S{suffix}", f"s-{suffix}"))
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id, is_active) "
                "VALUES (%s, %s, %s, %s, %s, %s, TRUE)",
                (product_id, f"POL-{suffix}", f"P{suffix}", brand_id, category_id, subcategory_id))
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, sales_unit, is_active, listing_status) "
                "VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')",
                (vendor_product_id, vendor_id, product_id, f"VP-{suffix}"))
    cur.execute("INSERT INTO vendor_inventory (vendor_product_id, inventory_unit, physical_quantity, reserved_quantity, moq, freshness_status) "
                "VALUES (%s, 'CARTON', 100, 0, 1, 'FRESH')",
                (vendor_product_id,))
    cur.execute("INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current) VALUES (%s, 500000, TRUE)",
                (vendor_product_id,))

    cur.execute(
        "INSERT INTO baskets (id, retailer_id, status, version) VALUES (%s, %s, %s, %s)",
        (basket_id, retailer_id, basket_status, version),
    )
    cur.execute(
        "INSERT INTO allocation_plans (id, basket_id, basket_version, status, strategy, vendor_count, total_estimated_toman, expires_at) "
        "VALUES (%s, %s, %s, %s, 'SINGLE_VENDOR', 1, 500000, now() + interval '%s minutes')",
        (plan_id, basket_id, plan_version, plan_status, expires_in_minutes),
    )
    basket_item_id = str(uuid4())
    cur.execute(
        "INSERT INTO basket_items (id, basket_id, product_id, requested_quantity, requested_unit, pack_quantity) VALUES (%s, %s, %s, 10, 'CARTON', 4)",
        (basket_item_id, basket_id, product_id),
    )
    cur.execute(
        "INSERT INTO allocation_items (id, allocation_plan_id, basket_item_id, vendor_id, vendor_product_id, "
        "allocated_quantity, allocated_unit, unit_price_snapshot_toman, line_total_toman, status) "
        "VALUES (%s, %s, %s, %s, %s, 10, 'CARTON', 500000, 5000000, 'ALLOCATED')",
        (allocation_item_id, plan_id, basket_item_id, vendor_id, vendor_product_id),
    )

    vendor_allocations = [{
        "vendor_id": vendor_id,
        "product_id": product_id,
        "vendor_product_id": vendor_product_id,
        "quantity": 10,
        "packaging_unit": "CARTON",
        "pack_quantity": 4,
        "unit_price_toman": 500000,
        "amount_toman": 5000000,
    }]

    return {
        "retailer_id": retailer_id, "basket_id": basket_id, "plan_id": plan_id,
        "vendor_id": vendor_id, "product_id": product_id,
        "vendor_allocations": vendor_allocations,
    }


def test_valid_checkout_passes():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8])
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            validate_allocation_against_basket(
                cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                data["vendor_allocations"],
            )
    finally:
        conn.close()


def test_wrong_retailer_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8])
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="does not own"):
                validate_allocation_against_basket(
                    cur, data["basket_id"], data["plan_id"], str(uuid4()),
                    data["vendor_allocations"],
                )
    finally:
        conn.close()


def test_submitted_basket_status_passes():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8], basket_status="SUBMITTED")
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            validate_allocation_against_basket(
                cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                data["vendor_allocations"],
            )
    finally:
        conn.close()


def test_wrong_basket_status_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8], basket_status="EXPIRED")
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="cannot be checked out"):
                validate_allocation_against_basket(
                    cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                    data["vendor_allocations"],
                )
    finally:
        conn.close()


def test_stale_plan_version_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8], version=2, plan_version=1)
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="stale"):
                validate_allocation_against_basket(
                    cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                    data["vendor_allocations"],
                )
    finally:
        conn.close()


def test_expired_plan_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8], expires_in_minutes=-5)
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="expired"):
                validate_allocation_against_basket(
                    cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                    data["vendor_allocations"],
                )
    finally:
        conn.close()


def test_non_confirmed_plan_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8], plan_status="PREVIEW")
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="not confirmed"):
                validate_allocation_against_basket(
                    cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                    data["vendor_allocations"],
                )
    finally:
        conn.close()


def test_allocation_count_mismatch_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8])
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="exactly one vendor"):
                validate_allocation_against_basket(
                    cur, data["basket_id"], data["plan_id"], data["retailer_id"],
                    [],
                )
    finally:
        conn.close()


def test_basket_not_found_rejected():
    conn = _db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            data = _seed_basket_and_plan(cur, uuid4().hex[:8])
        conn.commit()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            with pytest.raises(AllocationIntegrityError, match="not found"):
                validate_allocation_against_basket(
                    cur, str(uuid4()), data["plan_id"], data["retailer_id"],
                    data["vendor_allocations"],
                )
    finally:
        conn.close()
