"""PostgreSQL integration tests for canonical vendor full-order acceptance."""

from __future__ import annotations

import os
from uuid import uuid4

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from scripts.application_boundary import ApplicationContext, POLApplicationBoundary


@pytest.fixture
def pg_connection():
    conn = psycopg2.connect(
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
    try:
        yield conn
    finally:
        conn.close()


def _setup_order(cur, suffix: str):
    retailer_user = str(uuid4())
    retailer_org = str(uuid4())
    retailer_id = str(uuid4())
    vendor_user = str(uuid4())
    vendor_org = str(uuid4())
    vendor_id = str(uuid4())
    category_id = str(uuid4())
    subcategory_id = str(uuid4())
    brand_id = str(uuid4())
    product_id = str(uuid4())
    vendor_product_id = str(uuid4())
    basket_id = str(uuid4())
    plan_id = str(uuid4())
    group_id = str(uuid4())
    order_id = str(uuid4())
    order_item_id = str(uuid4())
    reservation_id = str(uuid4())

    cur.execute(
        """
        INSERT INTO users (id, phone_number, full_name, role)
        VALUES (%s, %s, 'Acceptance Retailer', 'RETAILER_OWNER')
        """,
        (retailer_user, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        """
        INSERT INTO organizations (id, name, org_type, status)
        VALUES (%s, %s, 'RETAILER', 'ACTIVE')
        """,
        (retailer_org, f"Acceptance Retailer {suffix}"),
    )
    cur.execute(
        """
        INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
        VALUES (%s, %s, %s, 'RETAILER_OWNER', 'ACTIVE')
        """,
        (str(uuid4()), retailer_org, retailer_user),
    )
    cur.execute(
        """
        INSERT INTO retailers (
            id, user_id, organization_id, store_name, city, neighborhood, address
        ) VALUES (%s, %s, %s, 'Acceptance Store', 'Ahvaz', 'Naderi', 'Test')
        """,
        (retailer_id, retailer_user, retailer_org),
    )

    cur.execute(
        """
        INSERT INTO users (id, phone_number, full_name, role)
        VALUES (%s, %s, 'Acceptance Vendor', 'VENDOR_OWNER')
        """,
        (vendor_user, f"+9891{uuid4().int % 100000000:08d}"),
    )
    cur.execute(
        """
        INSERT INTO organizations (id, name, org_type, status)
        VALUES (%s, %s, 'VENDOR', 'ACTIVE')
        """,
        (vendor_org, f"Acceptance Vendor {suffix}"),
    )
    cur.execute(
        """
        INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
        VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')
        """,
        (str(uuid4()), vendor_org, vendor_user),
    )
    cur.execute(
        """
        INSERT INTO vendors (
            id, user_id, organization_id, business_name,
            warehouse_address, min_order_value_toman, status
        ) VALUES (%s, %s, %s, 'Acceptance Vendor', 'Ahvaz Hub', 1000000, 'ACTIVE')
        """,
        (vendor_id, vendor_user, vendor_org),
    )

    cur.execute(
        """
        INSERT INTO categories (id, name_fa, slug)
        VALUES (%s, 'Acceptance Category', %s)
        """,
        (category_id, f"accept-cat-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO subcategories (id, category_id, name_fa, slug)
        VALUES (%s, %s, 'Acceptance Subcategory', %s)
        """,
        (subcategory_id, category_id, f"accept-sub-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO brands (id, name_fa, slug)
        VALUES (%s, 'Acceptance Brand', %s)
        """,
        (brand_id, f"accept-brand-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO products (
            id, master_sku, brand_id, category_id, subcategory_id,
            canonical_name_fa, is_active
        ) VALUES (%s, %s, %s, %s, %s, 'Acceptance Product', TRUE)
        """,
        (product_id, f"ACC-{suffix}", brand_id, category_id, subcategory_id),
    )
    cur.execute(
        """
        INSERT INTO vendor_products (
            id, vendor_id, product_id, vendor_sku, packaging_unit,
            pack_quantity, sales_unit, is_active, listing_status
        ) VALUES (%s, %s, %s, %s, 'CARTON', 4, 'CARTON', TRUE, 'ACTIVE')
        """,
        (vendor_product_id, vendor_id, product_id, f"ACC-VP-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO vendor_inventory (
            vendor_product_id, inventory_unit, physical_quantity,
            reserved_quantity, moq, freshness_status
        ) VALUES (%s, 'CARTON', 100, 10, 1, 'FRESH')
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

    cur.execute(
        """
        INSERT INTO baskets (id, retailer_id, status, version)
        VALUES (%s, %s, 'SUBMITTED', 1)
        """,
        (basket_id, retailer_id),
    )
    cur.execute(
        """
        INSERT INTO allocation_plans (
            id, basket_id, basket_version, status, strategy,
            vendor_count, total_estimated_toman, expires_at
        ) VALUES (
            %s, %s, 1, 'CONFIRMED', 'MULTI_VENDOR_MIN_FRAGMENTATION',
            1, 5000000, now() + interval '15 minutes'
        )
        """,
        (plan_id, basket_id),
    )
    cur.execute(
        """
        INSERT INTO order_groups (
            id, basket_id, allocation_plan_id, retailer_id,
            checkout_idempotency_key, total_amount_toman,
            order_count, group_status
        ) VALUES (
            %s, %s, %s, %s, %s, 5000000, 1, 'ACTIVE'
        )
        """,
        (group_id, basket_id, plan_id, retailer_id, f"accept-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO orders (
            id, order_group_id, allocation_plan_id, retailer_id, vendor_id,
            order_number, total_amount_toman, order_status, dispute_status,
            delivery_address_snapshot, correlation_id
        ) VALUES (
            %s, %s, %s, %s, %s, %s, 5000000, 'SUBMITTED', 'NONE',
            '{}'::jsonb, %s
        )
        """,
        (order_id, group_id, plan_id, retailer_id, vendor_id, f"ORD-ACC-{suffix}", suffix),
    )
    cur.execute(
        """
        INSERT INTO order_items (
            id, order_id, product_id, vendor_product_id,
            product_name_snapshot, brand_name_snapshot, vendor_sku_snapshot,
            packaging_unit_snapshot, pack_quantity_snapshot,
            ordered_quantity, accepted_quantity, delivered_quantity,
            unit_price_toman, total_line_amount_toman, fulfillment_status
        ) VALUES (
            %s, %s, %s, %s,
            'Acceptance Product', 'Acceptance Brand', %s,
            'CARTON', 4, 10, NULL, 0, 500000, 5000000, 'PENDING'
        )
        """,
        (order_item_id, order_id, product_id, vendor_product_id, f"ACC-VP-{suffix}"),
    )
    cur.execute(
        """
        INSERT INTO inventory_reservations (
            id, vendor_product_id, order_id, order_item_id,
            idempotency_key, quantity, status, expires_at
        ) VALUES (
            %s, %s, %s, %s, %s, 10, 'ACTIVE',
            now() + interval '15 minutes'
        )
        """,
        (reservation_id, vendor_product_id, order_id, order_item_id, f"res-{suffix}"),
    )

    return {
        "retailer_user": retailer_user,
        "retailer_org": retailer_org,
        "vendor_user": vendor_user,
        "vendor_org": vendor_org,
        "vendor_id": vendor_id,
        "vendor_product_id": vendor_product_id,
        "order_id": order_id,
        "order_item_id": order_item_id,
        "reservation_id": reservation_id,
    }


def test_vendor_full_accept_consumes_reservation_and_notifies_retailer(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            boundary = POLApplicationBoundary(
                cur,
                ApplicationContext(
                    user_id=data["vendor_user"],
                    organization_id=data["vendor_org"],
                    correlation_id=f"test-{suffix}",
                ),
            )

            result = boundary.vendor_order_accept(order_id=data["order_id"])

            assert result["order_status"] == "ACCEPTED"
            assert result["accepted_item_count"] == 1
            assert result["reservation_count"] == 1

            cur.execute(
                """
                SELECT order_status FROM orders WHERE id = %s
                """,
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "ACCEPTED"

            cur.execute(
                """
                SELECT accepted_quantity FROM order_items WHERE id = %s
                """,
                (data["order_item_id"],),
            )
            assert cur.fetchone()["accepted_quantity"] == 10

            cur.execute(
                """
                SELECT status FROM inventory_reservations WHERE id = %s
                """,
                (data["reservation_id"],),
            )
            assert cur.fetchone()["status"] == "CONSUMED"

            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                """,
                (data["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            assert inventory["physical_quantity"] == 90
            assert inventory["reserved_quantity"] == 0

            cur.execute(
                """
                SELECT COUNT(*) AS count
                FROM outbox_events
                WHERE event_name = 'ORDER_ACCEPTED'
                  AND aggregate_id = %s
                  AND target_user_id = %s
                  AND target_organization_id = %s
                  AND status = 'PENDING'
                """,
                (data["order_id"], data["retailer_user"], data["retailer_org"]),
            )
            assert cur.fetchone()["count"] == 1


def test_vendor_order_accept_is_tenant_protected(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)

            rogue_user = str(uuid4())
            rogue_org = str(uuid4())
            cur.execute(
                """
                INSERT INTO users (id, phone_number, full_name, role)
                VALUES (%s, %s, 'Rogue Vendor', 'VENDOR_OWNER')
                """,
                (rogue_user, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                """
                INSERT INTO organizations (id, name, org_type, status)
                VALUES (%s, %s, 'VENDOR', 'ACTIVE')
                """,
                (rogue_org, f"Rogue Vendor {suffix}"),
            )
            cur.execute(
                """
                INSERT INTO organization_memberships (id, organization_id, user_id, role, status)
                VALUES (%s, %s, %s, 'VENDOR_OWNER', 'ACTIVE')
                """,
                (str(uuid4()), rogue_org, rogue_user),
            )

            boundary = POLApplicationBoundary(
                cur,
                ApplicationContext(
                    user_id=rogue_user,
                    organization_id=rogue_org,
                    correlation_id=f"rogue-{suffix}",
                ),
            )
            with pytest.raises(PermissionError):
                boundary.vendor_order_accept(order_id=data["order_id"])

            cur.execute(
                """
                SELECT order_status FROM orders WHERE id = %s
                """,
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "SUBMITTED"


def test_vendor_order_accept_rejects_non_submitted_state_without_mutation(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)
            cur.execute(
                "UPDATE orders SET order_status = 'PREPARING' WHERE id = %s",
                (data["order_id"],),
            )
            boundary = POLApplicationBoundary(
                cur,
                ApplicationContext(
                    user_id=data["vendor_user"],
                    organization_id=data["vendor_org"],
                    correlation_id=f"state-{suffix}",
                ),
            )

            with pytest.raises(ValueError):
                boundary.vendor_order_accept(order_id=data["order_id"])

            cur.execute(
                "SELECT order_status FROM orders WHERE id = %s",
                (data["order_id"],),
            )
            assert cur.fetchone()["order_status"] == "PREPARING"

            cur.execute(
                "SELECT status FROM inventory_reservations WHERE id = %s",
                (data["reservation_id"],),
            )
            assert cur.fetchone()["status"] == "ACTIVE"

            cur.execute(
                """
                SELECT physical_quantity, reserved_quantity
                FROM vendor_inventory
                WHERE vendor_product_id = %s
                """,
                (data["vendor_product_id"],),
            )
            inventory = cur.fetchone()
            assert inventory["physical_quantity"] == 100
            assert inventory["reserved_quantity"] == 10
def test_vendor_staff_cannot_accept_order(pg_connection):
    suffix = uuid4().hex[:10]
    with pg_connection:
        with pg_connection.cursor(cursor_factory=RealDictCursor) as cur:
            data = _setup_order(cur, suffix)

            staff_user_id = str(uuid4())
            cur.execute(
                """
                INSERT INTO users (id, phone_number, full_name, role, is_active)
                VALUES (%s, %s, 'Acceptance Staff', 'VENDOR_STAFF', TRUE)
                """,
                (staff_user_id, f"+9891{uuid4().int % 100000000:08d}"),
            )
            cur.execute(
                """
                INSERT INTO organization_memberships
                    (id, organization_id, user_id, role, status, is_primary)
                VALUES (%s, %s, %s, 'VENDOR_STAFF', 'ACTIVE', FALSE)
                """,
                (str(uuid4()), data["vendor_org"], staff_user_id),
            )
            try:
                with pytest.raises(PermissionError):
                    POLApplicationBoundary(
                        cur,
                        ApplicationContext(
                            user_id=staff_user_id,
                            organization_id=data["vendor_org"],
                            correlation_id=f"staff-accept-{uuid4()}",
                        ),
                    ).vendor_order_accept(order_id=data["order_id"])

                cur.execute(
                    "SELECT order_status FROM orders WHERE id=%s",
                    (data["order_id"],),
                )
                assert cur.fetchone()["order_status"] == "SUBMITTED"
            finally:
                cur.execute("DELETE FROM users WHERE id=%s", (staff_user_id,))
