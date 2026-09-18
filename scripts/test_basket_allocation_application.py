"""PostgreSQL integration verification for the canonical basket/allocation boundary."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
from psycopg2.extras import RealDictCursor

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary


def _connect():
    return psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=int(
            os.environ.get("POL_API_DB_PORT")
            or os.environ.get("POL_PG_PORT")
            or os.environ.get("PGPORT", "5432")
        ),
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
        password=os.environ.get("POL_API_DB_PASSWORD") or os.environ.get("PGPASSWORD"),
    )


def test_basket_allocation_application_boundary_round_trip():
    conn = _connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        suffix = uuid4().hex[:10]

        retailer_user_id = str(uuid4())
        retailer_org_id = str(uuid4())
        vendor_user_id = str(uuid4())
        vendor_org_id = str(uuid4())
        retailer_id = str(uuid4())
        vendor_id = str(uuid4())
        category_id = str(uuid4())
        subcategory_id = str(uuid4())
        brand_id = str(uuid4())
        product_id = str(uuid4())
        vendor_product_id = str(uuid4())

        cur.execute(
            """
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'HTTP Basket Retailer', 'RETAILER_OWNER')
            """,
            (retailer_user_id, f"+9891{uuid4().int % 100000000:08d}"),
        )
        cur.execute(
            """
            INSERT INTO organizations (id, name, org_type, status)
            VALUES (%s, %s, 'RETAILER', 'ACTIVE')
            """,
            (retailer_org_id, f"HTTP Basket Retailer {suffix}"),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships (
                id, organization_id, user_id, role, status
            )
            VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')
            """,
            (str(uuid4()), retailer_org_id, retailer_user_id),
        )
        cur.execute(
            """
            INSERT INTO retailers (
                id, user_id, organization_id, store_name, city,
                neighborhood, address
            )
            VALUES (%s, %s, %s, 'HTTP Basket Store', 'Ahvaz', 'Naderi', 'Test')
            """,
            (retailer_id, retailer_user_id, retailer_org_id),
        )

        cur.execute(
            """
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'HTTP Basket Vendor', 'VENDOR_OWNER')
            """,
            (vendor_user_id, f"+9891{uuid4().int % 100000000:08d}"),
        )
        cur.execute(
            """
            INSERT INTO organizations (id, name, org_type, status)
            VALUES (%s, %s, 'VENDOR', 'ACTIVE')
            """,
            (vendor_org_id, f"HTTP Basket Vendor {suffix}"),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships (
                id, organization_id, user_id, role, status
            )
            VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')
            """,
            (str(uuid4()), vendor_org_id, vendor_user_id),
        )
        cur.execute(
            """
            INSERT INTO vendors (
                id, user_id, organization_id, business_name,
                warehouse_address, min_order_value_toman, status
            )
            VALUES (%s, %s, %s, 'HTTP Basket Vendor', 'Ahvaz Hub', 1000000, 'ACTIVE')
            """,
            (vendor_id, vendor_user_id, vendor_org_id),
        )

        cur.execute(
            """
            INSERT INTO categories (id, name_fa, slug)
            VALUES (%s, 'HTTP Test Category', %s)
            """,
            (category_id, f"http-cat-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO subcategories (id, category_id, name_fa, slug)
            VALUES (%s, %s, 'HTTP Test Subcategory', %s)
            """,
            (subcategory_id, category_id, f"http-sub-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO brands (id, name_fa, slug)
            VALUES (%s, 'HTTP Test Brand', %s)
            """,
            (brand_id, f"http-brand-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO products (
                id, master_sku, brand_id, category_id, subcategory_id,
                canonical_name_fa, is_active
            )
            VALUES (%s, %s, %s, %s, %s, 'HTTP Test Product', TRUE)
            """,
            (product_id, f"HTTP-{suffix}", brand_id, category_id, subcategory_id),
        )
        cur.execute(
            """
            INSERT INTO vendor_products (
                id, vendor_id, product_id, vendor_sku, packaging_unit,
                pack_quantity, sales_unit, is_active, listing_status
            )
            VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')
            """,
            (vendor_product_id, vendor_id, product_id, f"HTTP-VP-{suffix}"),
        )
        cur.execute(
            """
            INSERT INTO vendor_inventory (
                vendor_product_id, inventory_unit, physical_quantity,
                reserved_quantity, moq, freshness_status
            )
            VALUES (%s, 'CARTON', 100, 0, 1, 'FRESH')
            """,
            (vendor_product_id,),
        )
        cur.execute(
            """
            INSERT INTO vendor_prices (vendor_product_id, price_toman, is_current)
            VALUES (%s, 500000, TRUE)
            """,
            (vendor_product_id,),
        )

        boundary = POLApplicationBoundary(
            cur,
            ApplicationContext(
                user_id=retailer_user_id,
                organization_id=retailer_org_id,
                correlation_id=f"test-{suffix}",
            ),
        )

        created = boundary.basket_create()
        basket_id = created["basket_id"]
        assert created == {
            "basket_id": basket_id,
            "version": 1,
            "status": "OPEN",
        }

        added = boundary.basket_add_item(
            basket_id=basket_id,
            product_id=product_id,
            quantity=10,
            pack_quantity=4,
            expected_version=1,
        )
        assert added["version"] == 2

        preview = boundary.basket_allocation_preview(basket_id=basket_id)
        assert preview["vendor_count"] == 1
        assert preview["summary"]["total_items_requested"] == 10
        assert preview["summary"]["total_items_allocated"] == 10
        assert preview["summary"]["total_amount_toman"] == 5000000
        assert preview["unfulfilled_items"] == []

        cur.execute(
            """
            SELECT id, status, basket_version, vendor_count, total_estimated_toman
            FROM allocation_plans
            WHERE id = %s
            """,
            (preview["allocation_plan_id"],),
        )
        plan = cur.fetchone()
        assert plan["status"] == "CONFIRMED"
        assert plan["basket_version"] == 2
        assert plan["vendor_count"] == 1
        assert plan["total_estimated_toman"] == 5000000

        cur.execute(
            """
            SELECT COUNT(*) AS count
            FROM allocation_items
            WHERE allocation_plan_id = %s
              AND status = 'ALLOCATED'
              AND vendor_id = %s
              AND vendor_product_id = %s
              AND allocated_quantity = 10
              AND unit_price_snapshot_toman = 500000
            """,
            (preview["allocation_plan_id"], vendor_id, vendor_product_id),
        )
        assert cur.fetchone()["count"] == 1
    finally:
        conn.rollback()
        cur.close()
        conn.close()
