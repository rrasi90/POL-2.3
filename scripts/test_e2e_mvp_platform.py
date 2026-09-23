import hashlib
import json
import os
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import psycopg2
import pytest
from psycopg2 import sql
from psycopg2.extensions import parse_dsn
from psycopg2.extras import RealDictCursor

from scripts.allocation_engine import BasketItem, MultiVendorAllocationEngine, Vendor, VendorSKU
from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.migration_runner import apply_migration_chain, get_migration_chain
from scripts import operational_policies
from scripts.operational_policies import AllocationIntegrityError, validate_vendor_operational_capacity


@pytest.fixture
def postgres_database():
    dsn = os.environ.get("POL_E2E_PG_DSN")
    if not dsn:
        pytest.fail("Parent must supply POL_E2E_PG_DSN for an isolated PostgreSQL 18 server; no local fallback.")
    config = parse_dsn(dsn)
    if not all(config.get(key) for key in ("host", "port", "dbname", "user")):
        pytest.fail("POL_E2E_PG_DSN must explicitly specify host, port, dbname and user.")
    database = f"pol_e2e_{uuid4().hex}"
    admin = psycopg2.connect(**dict(config, connect_timeout=5))
    admin.autocommit = True
    created = False
    try:
        assert admin.server_version // 10000 == 18, "D-015 requires PostgreSQL 18."
        with admin.cursor() as cur:
            cur.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(database)))
        created = True
        test_config = dict(config, dbname=database, connect_timeout=5, options="-c search_path=public")
        conn = psycopg2.connect(**test_config)
        try:
            apply_migration_chain(conn, get_migration_chain(), verbose=False)
            conn.commit()
        finally:
            conn.close()
        yield test_config
    finally:
        try:
            if created:
                with admin.cursor() as cur:
                    cur.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(database)))
        finally:
            admin.close()


@contextmanager
def transaction(config):
    conn = psycopg2.connect(**config)
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
    finally:
        conn.close()


def insert_row(cur, table, **values):
    cur.execute(
        sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(
            sql.Identifier(table),
            sql.SQL(", ").join(map(sql.Identifier, values)),
            sql.SQL(", ").join(sql.Placeholder() for _ in values),
        ),
        tuple(values.values()),
    )
    return cur.fetchone()


@pytest.fixture
def checkout_catalog(postgres_database):
    with transaction(postgres_database) as cur:
        actors = []
        for index, org_type in enumerate(("RETAILER", "VENDOR", "VENDOR")):
            user = insert_row(
                cur, "users", phone_number=f"+98916000000{index}",
                role=f"{org_type}_OWNER", full_name=f"Batch1 {org_type} {index}",
            )
            org = insert_row(cur, "organizations", name=f"Batch1 {index}", org_type=org_type, status="ACTIVE")
            insert_row(
                cur, "organization_memberships", organization_id=org["id"],
                user_id=user["id"], role=f"{org_type}_OWNER", status="ACTIVE",
            )
            actors.append((str(user["id"]), str(org["id"])))
        retailer = insert_row(
            cur, "retailers", user_id=actors[0][0], organization_id=actors[0][1],
            store_name="Batch1 retailer", city="Ahvaz", neighborhood="Naderi", address="Batch1 address",
        )
        vendor_ids = []
        for index, (user_id, organization_id) in enumerate(actors[1:]):
            vendor = insert_row(
                cur, "vendors", user_id=user_id, organization_id=organization_id,
                business_name=f"Batch1 vendor {index}", warehouse_address="Ahvaz hub",
                min_order_value_toman=1000000, status="ACTIVE",
            )
            vendor_ids.append(str(vendor["id"]))
            insert_row(cur, "vendor_capacity_profiles", vendor_id=vendor["id"], timezone="UTC")
        brand = insert_row(cur, "brands", name_fa="برند آزمون", slug="batch1-brand")
        category = insert_row(cur, "categories", name_fa="مواد غذایی", slug="batch1-food")
        subcategory = insert_row(
            cur, "subcategories", category_id=category["id"], name_fa="آزمون", slug="batch1-subcategory",
        )
        lines = []
        for index, (vendor_id, name, unit, pack, quantity, price) in enumerate((
            (vendor_ids[0], "برنج آزمون", "CARTON", 6, 3, 500000),
            (vendor_ids[0], "روغن آزمون", "BOX", 4, 4, 400000),
            (vendor_ids[1], "چای آزمون", "PACK", 8, 5, 300000),
        )):
            product = insert_row(
                cur, "products", master_sku=f"BATCH1-{index}", canonical_name_fa=name,
                brand_id=brand["id"], category_id=category["id"], subcategory_id=subcategory["id"],
                default_pack_unit=unit, default_pack_quantity=pack, is_verified=True,
            )
            offer = insert_row(
                cur, "vendor_products", vendor_id=vendor_id, product_id=product["id"],
                vendor_sku=f"BATCH1-SKU-{index}", packaging_unit=unit, pack_quantity=pack,
                sales_unit=unit, is_active=True, listing_status="ACTIVE",
            )
            insert_row(
                cur, "vendor_inventory", vendor_product_id=offer["id"], inventory_unit=unit,
                physical_quantity=100, reserved_quantity=0, moq=2,
            )
            insert_row(cur, "vendor_prices", vendor_product_id=offer["id"], price_toman=price, is_current=True)
            lines.append({
                "product_id": str(product["id"]), "vendor_product_id": str(offer["id"]),
                "vendor_id": vendor_id, "quantity": quantity, "unit_price_toman": price,
                "product_name_snapshot": name, "brand_name_snapshot": brand["name_fa"],
                "vendor_sku_snapshot": offer["vendor_sku"], "packaging_unit_snapshot": unit,
                "pack_quantity_snapshot": pack,
            })
    return {
        "retailer_id": str(retailer["id"]), "lines": lines,
        "context": ApplicationContext(actors[0][0], actors[0][1], f"batch1-{uuid4().hex}"),
    }


def persist_request(cur, catalog):
    basket = insert_row(cur, "baskets", retailer_id=catalog["retailer_id"], status="OPEN", version=1)
    basket_items = []
    for line in catalog["lines"]:
        row = insert_row(
            cur, "basket_items", basket_id=basket["id"], product_id=line["product_id"],
            requested_quantity=line["quantity"], requested_unit=line["packaging_unit_snapshot"],
            pack_quantity=line["pack_quantity_snapshot"],
        )
        basket_items.append(BasketItem(
            str(row["id"]), str(row["product_id"]), row["requested_quantity"], row["requested_unit"],
        ))
    cur.execute("SELECT id, business_name, status, min_order_value_toman FROM vendors ORDER BY id")
    vendors = {
        str(row["id"]): Vendor(
            id=str(row["id"]), name=row["business_name"], active=row["status"] == "ACTIVE",
            mov_toman=row["min_order_value_toman"], delivery_zones=("Ahvaz",),
        )
        for row in cur.fetchall()
    }
    cur.execute("""
        SELECT vp.id, vp.vendor_id, vp.product_id, vp.packaging_unit,
               p.price_toman, i.physical_quantity, i.reserved_quantity, i.moq
        FROM vendor_products vp
        JOIN vendor_inventory i ON i.vendor_product_id = vp.id
        JOIN vendor_prices p ON p.vendor_product_id = vp.id AND p.is_current = TRUE
        ORDER BY vp.id
    """)
    skus = [VendorSKU(
        str(row["id"]), str(row["vendor_id"]), str(row["product_id"]), row["packaging_unit"],
        row["price_toman"], row["physical_quantity"], row["reserved_quantity"], row["moq"],
    ) for row in cur.fetchall()]
    engine = MultiVendorAllocationEngine(vendors, skus)
    plan = engine.allocate(catalog["retailer_id"], "Ahvaz", basket_items)
    repeated = engine.allocate(catalog["retailer_id"], "Ahvaz", basket_items)
    assert plan.items == repeated.items
    assert plan.vendor_subtotals == repeated.vendor_subtotals
    assert plan.total_amount_toman == repeated.total_amount_toman == 4600000
    assert plan.is_fully_fulfilled and not plan.unfulfilled_items
    assert plan.vendor_count == repeated.vendor_count == 2
    assert len(plan.allocated_items) == 3
    assert sorted(Counter(item.vendor_id for item in plan.items).values()) == [1, 2]
    assert {
        (item.master_product_id, item.vendor_sku_id, item.requested_quantity)
        for item in plan.items
    } == {
        (line["product_id"], line["vendor_product_id"], line["quantity"])
        for line in catalog["lines"]
    }
    cur.execute("SELECT now() + interval '15 minutes' AS expires_at")
    expires_at = cur.fetchone()["expires_at"]
    insert_row(
        cur, "allocation_plans", id=plan.plan_id, basket_id=basket["id"], status="CONFIRMED",
        basket_version=basket["version"], expires_at=expires_at, vendor_count=plan.vendor_count,
        total_estimated_toman=plan.total_amount_toman,
    )
    for item in plan.items:
        insert_row(
            cur, "allocation_items", allocation_plan_id=plan.plan_id, basket_item_id=item.basket_item_id,
            vendor_id=item.vendor_id, vendor_product_id=item.vendor_sku_id,
            allocated_quantity=item.requested_quantity, allocated_unit=item.packaging_unit,
            unit_price_snapshot_toman=item.unit_price_toman, line_total_toman=item.total_price_toman,
            status=item.status,
        )
    return {
        "basket_id": str(basket["id"]), "plan_id": plan.plan_id, "retailer_id": catalog["retailer_id"],
        "idempotency_key": f"batch1-{uuid4().hex}",
        "address_snapshot": {"city": "Ahvaz", "address": "نشانی آزمون", "postal_code": "6130000000"},
        "vendor_allocations": [{
            "vendor_id": item.vendor_id, "vendor_product_id": item.vendor_sku_id,
            "quantity": item.requested_quantity, "unit_price_toman": item.unit_price_toman,
            "amount_toman": item.total_price_toman,
        } for item in plan.allocated_items],
    }


@pytest.fixture
def checkout_request(postgres_database, checkout_catalog):
    with transaction(postgres_database) as cur:
        return persist_request(cur, checkout_catalog)


def snapshot(cur):
    state = {}
    for table in (
        "order_groups", "orders", "order_items", "inventory_reservations", "vendor_inventory",
        "outbox_events", "baskets", "basket_items", "allocation_plans", "allocation_items",
    ):
        cur.execute(sql.SQL("SELECT * FROM {} ORDER BY id").format(sql.Identifier(table)))
        state[table] = [dict(row) for row in cur.fetchall()]
    cur.execute("""
        SELECT checkout_idempotency_key, checkout_request_fingerprint, id
        FROM order_groups ORDER BY checkout_idempotency_key
    """)
    state["idempotency"] = [dict(row) for row in cur.fetchall()]
    return state


def fingerprint(request):
    payload = {key: value for key, value in request.items() if key != "idempotency_key"}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_checkout(cur, catalog, request, result):
    group_id = result["order_group_id"]
    UUID(str(group_id))
    assert result["order_count"] == 2
    assert not result.get("idempotent_replay", False)
    cur.execute("SELECT * FROM order_groups WHERE id = %s", (group_id,))
    group = cur.fetchone()
    assert str(group["basket_id"]) == request["basket_id"]
    assert str(group["allocation_plan_id"]) == request["plan_id"]
    assert str(group["retailer_id"]) == catalog["retailer_id"]
    assert group["checkout_idempotency_key"] == request["idempotency_key"]
    assert group["checkout_request_fingerprint"] == fingerprint(request)
    assert (group["total_amount_toman"], group["order_count"], group["group_status"]) == (4600000, 2, "ACTIVE")
    cur.execute("""
        SELECT bi.product_id, bi.requested_quantity, bi.requested_unit, bi.pack_quantity,
               ai.vendor_id, ai.vendor_product_id, ai.allocated_quantity, ai.allocated_unit,
               ai.unit_price_snapshot_toman, ai.line_total_toman, ai.status
        FROM allocation_items ai
        JOIN basket_items bi ON bi.id = ai.basket_item_id
        WHERE ai.allocation_plan_id = %s AND bi.basket_id = %s
    """, (request["plan_id"], request["basket_id"]))
    allocated = cur.fetchall()
    assert len(allocated) == 3
    assert {tuple(row.values()) for row in allocated} == {
        (
            line["product_id"], line["quantity"], line["packaging_unit_snapshot"],
            line["pack_quantity_snapshot"], line["vendor_id"], line["vendor_product_id"],
            line["quantity"], line["packaging_unit_snapshot"], line["unit_price_toman"],
            line["quantity"] * line["unit_price_toman"], "ALLOCATED",
        )
        for line in catalog["lines"]
    }
    cur.execute("SELECT * FROM orders WHERE order_group_id = %s ORDER BY vendor_id", (group_id,))
    orders = cur.fetchall()
    assert len(orders) == len(result["orders"]) == 2
    assert {str(row["id"]) for row in orders} == {str(row["id"]) for row in result["orders"]}
    assert {str(row["vendor_id"]) for row in orders} == {line["vendor_id"] for line in catalog["lines"]}
    seen_products = []
    for order in orders:
        lines = [line for line in catalog["lines"] if line["vendor_id"] == str(order["vendor_id"])]
        assert str(order["retailer_id"]) == catalog["retailer_id"]
        assert order["order_status"] == "SUBMITTED"
        assert order["dispute_status"] == "NONE"
        assert order["delivery_address_snapshot"] == request["address_snapshot"]
        assert order["total_amount_toman"] == sum(line["quantity"] * line["unit_price_toman"] for line in lines)
        assert order["commission_rate"] == order["commission_amount_toman"] == 0
        cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order["id"],))
        items = cur.fetchall()
        assert len(items) == len(lines)
        by_offer = {str(item["vendor_product_id"]): item for item in items}
        assert set(by_offer) == {line["vendor_product_id"] for line in lines}
        for line in lines:
            item = dict(by_offer[line["vendor_product_id"]])
            UUID(str(item.pop("id")))
            assert item.pop("created_at") == order["created_at"] == group["created_at"]
            assert item == {
                "order_id": order["id"], "product_id": line["product_id"],
                "vendor_product_id": line["vendor_product_id"],
                "product_name_snapshot": line["product_name_snapshot"],
                "brand_name_snapshot": line["brand_name_snapshot"],
                "vendor_sku_snapshot": line["vendor_sku_snapshot"],
                "packaging_unit_snapshot": line["packaging_unit_snapshot"],
                "pack_quantity_snapshot": line["pack_quantity_snapshot"],
                "ordered_quantity": line["quantity"], "accepted_quantity": None, "delivered_quantity": 0,
                "unit_price_toman": line["unit_price_toman"],
                "total_line_amount_toman": line["quantity"] * line["unit_price_toman"],
                "fulfillment_status": "PENDING", "dispute_reason": None,
            }
            seen_products.append(str(item["product_id"]))
        cur.execute("SELECT * FROM inventory_reservations WHERE order_id = %s", (order["id"],))
        reservations = cur.fetchall()
        assert len(reservations) == len(lines)
        by_offer = {str(row["vendor_product_id"]): row for row in reservations}
        assert set(by_offer) == {line["vendor_product_id"] for line in lines}
        for line in lines:
            reservation = by_offer[line["vendor_product_id"]]
            UUID(str(reservation["id"]))
            assert reservation["quantity"] == line["quantity"]
            assert reservation["status"] == "ACTIVE"
            assert reservation["idempotency_key"] == f"res-{request['idempotency_key']}-{line['vendor_product_id']}"
            assert reservation["order_item_id"] is None
            assert reservation["released_at"] is reservation["consumed_at"] is None
            assert reservation["created_at"] == group["created_at"]
            assert reservation["expires_at"] - reservation["created_at"] == timedelta(minutes=15)
    assert Counter(seen_products) == Counter({line["product_id"]: 1 for line in catalog["lines"]})


def assert_inventory(cur, catalog, checkouts):
    cur.execute("SELECT * FROM vendor_inventory")
    rows = cur.fetchall()
    assert len(rows) == 3
    by_offer = {str(row["vendor_product_id"]): row for row in rows}
    for line in catalog["lines"]:
        inventory = by_offer[line["vendor_product_id"]]
        assert inventory["physical_quantity"] == 100
        assert inventory["reserved_quantity"] == line["quantity"] * checkouts
        assert inventory["available_quantity"] == 100 - line["quantity"] * checkouts


def test_checkout_persists_multivendor_orders_snapshots_and_reservations(
    postgres_database, checkout_catalog, checkout_request,
):
    with transaction(postgres_database) as cur:
        result = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        assert_checkout(cur, checkout_catalog, checkout_request, result)
        assert_inventory(cur, checkout_catalog, 1)
        state = snapshot(cur)
        assert [len(state[table]) for table in (
            "order_groups", "orders", "order_items", "inventory_reservations", "idempotency",
        )] == [1, 2, 3, 3, 1]
        assert Counter(row["event_name"] for row in state["outbox_events"]) == Counter({
            "ORDER_GROUP_SUBMITTED": 1, "ORDER_SUBMITTED": 2,
        })
        cur.execute("UPDATE products SET canonical_name_fa = 'Changed live product'")
        cur.execute("UPDATE brands SET name_fa = 'Changed live brand'")
        cur.execute("UPDATE vendor_products SET vendor_sku = vendor_sku || '-changed', pack_quantity = pack_quantity + 1")
    with transaction(postgres_database) as cur:
        assert_checkout(cur, checkout_catalog, checkout_request, result)


def test_checkout_replay_fingerprint_and_new_request_same_retailer(
    postgres_database, checkout_catalog, checkout_request,
):
    with transaction(postgres_database) as cur:
        first = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        cur.execute("SELECT txid_current() AS id")
        first_transaction = cur.fetchone()["id"]
    with transaction(postgres_database) as cur:
        before = snapshot(cur)
    with transaction(postgres_database) as cur:
        replay = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        cur.execute("SELECT txid_current() AS id")
        assert cur.fetchone()["id"] != first_transaction
        assert replay["idempotent_replay"] is True
        assert str(replay["order_group"]["id"]) == str(first["order_group_id"])
        assert {
            str(row["id"]): dict(row) for row in replay["orders"]
        } == {str(row["id"]): dict(row) for row in first["orders"]}
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before
    altered = deepcopy(checkout_request)
    altered["address_snapshot"]["address"] = "Different destination"
    with pytest.raises(ValueError, match="different checkout request payload"):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**altered)
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before
        second_request = persist_request(cur, checkout_catalog)
    assert second_request["retailer_id"] == checkout_request["retailer_id"]
    for key in ("basket_id", "plan_id", "idempotency_key"):
        assert second_request[key] != checkout_request[key]
    with transaction(postgres_database) as cur:
        second = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(second_request))
    with transaction(postgres_database) as cur:
        assert_checkout(cur, checkout_catalog, checkout_request, first)
        assert_checkout(cur, checkout_catalog, second_request, second)
        assert second["order_group_id"] != first["order_group_id"]
        assert {str(row["id"]) for row in first["orders"]}.isdisjoint(str(row["id"]) for row in second["orders"])
        assert_inventory(cur, checkout_catalog, 2)
        after = snapshot(cur)
        assert [len(after[table]) for table in (
            "order_groups", "orders", "order_items", "inventory_reservations", "idempotency",
        )] == [2, 4, 6, 6, 2]
        assert after["outbox_events"] != before["outbox_events"]
        assert Counter(row["event_name"] for row in after["outbox_events"]) == Counter({
            "ORDER_GROUP_SUBMITTED": 2, "ORDER_SUBMITTED": 4,
        })


def test_checkout_rolls_back_after_partial_sql_writes(
    postgres_database, checkout_catalog, checkout_request,
):
    with transaction(postgres_database) as cur:
        before = snapshot(cur)
    with pytest.raises(psycopg2.errors.RaiseException, match="batch1 checkout fault") as failure:
        with transaction(postgres_database) as cur:
            cur.execute("""
                CREATE FUNCTION pg_temp.batch1_checkout_fault() RETURNS trigger
                LANGUAGE plpgsql AS $$
                DECLARE
                    evidence json;
                BEGIN
                    IF (SELECT count(*) FROM inventory_reservations) = 3 THEN
                        SELECT json_build_object(
                            'groups', (SELECT count(*) FROM order_groups),
                            'orders', (SELECT count(*) FROM orders),
                            'items', (SELECT count(*) FROM order_items),
                            'reservations', (SELECT count(*) FROM inventory_reservations),
                            'reserved_quantity', (SELECT sum(reserved_quantity) FROM vendor_inventory),
                            'idempotency', (SELECT count(*) FROM order_groups
                                WHERE checkout_idempotency_key IS NOT NULL
                                  AND checkout_request_fingerprint IS NOT NULL),
                            'outbox', (SELECT count(*) FROM outbox_events)
                        ) INTO evidence;
                        RAISE EXCEPTION 'batch1 checkout fault' USING DETAIL = evidence::text;
                    END IF;
                    RETURN NEW;
                END;
                $$;
                CREATE TRIGGER batch1_checkout_fault
                AFTER UPDATE OF reserved_quantity ON vendor_inventory
                FOR EACH ROW EXECUTE FUNCTION pg_temp.batch1_checkout_fault();
            """)
            POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    assert json.loads(failure.value.diag.message_detail) == {
        "groups": 1, "orders": 2, "items": 3, "reservations": 3,
        "reserved_quantity": 12, "idempotency": 1, "outbox": 0,
    }
    with transaction(postgres_database) as cur:
        assert snapshot(cur) == before
        assert_inventory(cur, checkout_catalog, 0)
        cur.execute("SELECT 1 FROM pg_trigger WHERE tgname = 'batch1_checkout_fault'")
        assert cur.fetchone() is None
    with transaction(postgres_database) as cur:
        retry = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        assert_checkout(cur, checkout_catalog, checkout_request, retry)
        assert_inventory(cur, checkout_catalog, 1)
        after = snapshot(cur)
        assert [len(after[table]) for table in (
            "order_groups", "orders", "order_items", "inventory_reservations", "idempotency",
        )] == [1, 2, 3, 3, 1]
        assert Counter(row["event_name"] for row in after["outbox_events"]) == Counter({
            "ORDER_GROUP_SUBMITTED": 1, "ORDER_SUBMITTED": 2,
        })

def test_hourly_capacity_uses_ordered_quantity_and_rejects_at_threshold(
    postgres_database, checkout_catalog, checkout_request,
):
    with transaction(postgres_database) as cur:
        cur.execute(
            "UPDATE vendor_capacity_profiles SET max_pick_units_per_hour = 5 WHERE vendor_id = %s",
            (checkout_catalog["lines"][0]["vendor_id"],),
        )
    with pytest.raises(AllocationIntegrityError, match="hourly pick capacity exhausted"):
        with transaction(postgres_database) as cur:
            POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        cur.execute("SELECT count(*) AS c FROM order_groups")
        assert cur.fetchone()["c"] == 0
        cur.execute("SELECT count(*) AS c FROM outbox_events")
        assert cur.fetchone()["c"] == 0
        cur.execute("UPDATE vendor_capacity_profiles SET max_pick_units_per_hour = 7")
    with transaction(postgres_database) as cur:
        POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
    with transaction(postgres_database) as cur:
        cur.execute(
            """
            SELECT sum(oi.ordered_quantity) AS units
            FROM order_items oi JOIN orders o ON o.id = oi.order_id
            WHERE o.vendor_id = %s
            """,
            (checkout_catalog["lines"][0]["vendor_id"],),
        )
        assert cur.fetchone()["units"] == 7


@pytest.mark.parametrize("status,age_minutes,limit,allowed", [
    ("SUBMITTED", 30, 13, False),
    ("SUBMITTED", 30, 14, True),
    ("CANCELLED", 30, 7, True),
    ("REJECTED", 30, 7, True),
    ("SUBMITTED", 61, 7, True),
])
def test_hourly_capacity_counts_recent_orders(
    postgres_database, checkout_catalog, checkout_request, status, age_minutes, limit, allowed,
):
    vendor_id = checkout_catalog["lines"][0]["vendor_id"]
    with transaction(postgres_database) as cur:
        first = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        cur.execute(
            "UPDATE orders SET order_status=%s, created_at=now() - %s * interval '1 minute' WHERE vendor_id=%s",
            (status, age_minutes, vendor_id),
        )
        cur.execute(
            "UPDATE vendor_capacity_profiles SET max_pick_units_per_hour=%s WHERE vendor_id=%s",
            (limit, vendor_id),
        )
        request = persist_request(cur, checkout_catalog)
    if allowed:
        with transaction(postgres_database) as cur:
            second = POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(request))
            assert second["order_group_id"] != first["order_group_id"]
    else:
        with transaction(postgres_database) as cur:
            before = snapshot(cur)
        with pytest.raises(AllocationIntegrityError, match="hourly pick capacity exhausted: 14 > 13"):
            with transaction(postgres_database) as cur:
                POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(request))
        with transaction(postgres_database) as cur:
            assert snapshot(cur) == before


def freeze_policy_clock(monkeypatch, instant):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)

    monkeypatch.setattr(operational_policies, "datetime", FixedDatetime)


@pytest.mark.parametrize("created_at,status,allowed", [
    ("2026-09-16T20:29:59+00:00", "SUBMITTED", True),
    ("2026-09-16T20:30:00+00:00", "SUBMITTED", False),
    ("2026-09-17T20:30:00+00:00", "SUBMITTED", True),
    ("2026-09-16T20:30:00+00:00", "CANCELLED", True),
    ("2026-09-16T20:30:00+00:00", "REJECTED", True),
])
def test_daily_capacity_uses_vendor_local_day(
    postgres_database, checkout_catalog, checkout_request, monkeypatch, created_at, status, allowed,
):
    vendor_id = checkout_catalog["lines"][0]["vendor_id"]
    with transaction(postgres_database) as cur:
        POLApplicationBoundary(cur, checkout_catalog["context"]).checkout(**deepcopy(checkout_request))
        cur.execute(
            "UPDATE orders SET created_at=%s, order_status=%s WHERE vendor_id=%s",
            (datetime.fromisoformat(created_at), status, vendor_id),
        )
        cur.execute(
            "UPDATE vendor_capacity_profiles SET timezone='Asia/Tehran', max_orders_per_day=1 WHERE vendor_id=%s",
            (vendor_id,),
        )
    freeze_policy_clock(monkeypatch, datetime(2026, 9, 16, 21, tzinfo=timezone.utc))
    allocations = [{"vendor_id": vendor_id, "quantity": 7, "amount_toman": 3100000}]
    with transaction(postgres_database) as cur:
        if allowed:
            validate_vendor_operational_capacity(cur, allocations)
        else:
            with pytest.raises(AllocationIntegrityError, match="daily order capacity exhausted: 2 > 1"):
                validate_vendor_operational_capacity(cur, allocations)


@pytest.mark.parametrize("instant,allowed", [
    ("2026-09-16T19:30:00+00:00", True),
    ("2026-09-16T21:30:00+00:00", True),
    ("2026-09-17T00:00:00+00:00", False),
])
def test_overnight_operating_window_remains_enforced(
    postgres_database, checkout_catalog, monkeypatch, instant, allowed,
):
    vendor_id = checkout_catalog["lines"][0]["vendor_id"]
    with transaction(postgres_database) as cur:
        cur.execute("UPDATE vendor_capacity_profiles SET timezone='Asia/Tehran' WHERE vendor_id=%s", (vendor_id,))
        for weekday in (3, 4):
            insert_row(
                cur, "vendor_operating_windows", vendor_id=vendor_id, weekday=weekday,
                timezone="Asia/Tehran", opens_at="22:00", closes_at="02:00", is_active=True,
            )
    freeze_policy_clock(monkeypatch, datetime.fromisoformat(instant))
    allocations = [{"vendor_id": vendor_id, "quantity": 7, "amount_toman": 3100000}]
    with transaction(postgres_database) as cur:
        if allowed:
            validate_vendor_operational_capacity(cur, allocations)
        else:
            with pytest.raises(AllocationIntegrityError, match="outside its operating window"):
                validate_vendor_operational_capacity(cur, allocations)
