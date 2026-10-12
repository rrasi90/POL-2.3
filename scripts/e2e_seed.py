"""Deterministic PostgreSQL fixture for browser E2E (TODO-006).

Idempotent and safe to re-run against `pol_test`. Creates:
  * 24 retailer accounts (phone pool +989123456000..023), each with its own
    organization, primary RETAILER_OWNER membership and retailer row;
  * one ACTIVE vendor account with three listed products that have live
    inventory and exactly one current price each;
  * a shared brand/category/subcategory tree for the three E2E products.

Every run also closes OPEN baskets left behind by a previous run and clears
OTP challenges for the seeded phone pool, so each browser test starts from a
known-clean server state.

Run:  python scripts/e2e_seed.py
"""

from __future__ import annotations

import json
import os
import uuid

import psycopg2
from psycopg2.extras import RealDictCursor

# Fixed namespace => stable UUIDs across machines and CI runs.
NAMESPACE = uuid.UUID("b6a58a9a-0d0e-4f3a-8f5a-6d1c4a2e9f11")

RETAILER_COUNT = 24
RETAILER_PHONE_PREFIX = "+989123456"  # + 3 digits => valid E.164, VARCHAR(15)
VENDOR_PHONE = "+989123457000"

PACK_QUANTITY = 12
PRICE_TOMAN = 250_000
PHYSICAL_QUANTITY = 500
MIN_ORDER_VALUE_TOMAN = 0

PRODUCTS = (
    ("POL-E2E-1001", "برنج دانا ۱۰ کیلوگرمی"),
    ("POL-E2E-1002", "روغن سرخ‌کردنی ۱٫۸ لیتری"),
    ("POL-E2E-1003", "ماکارونی رشته‌ای ۷۰۰ گرمی"),
)


def retailer_phones() -> list[str]:
    """Phone pool shared with the Playwright helpers."""
    return [f"{RETAILER_PHONE_PREFIX}{i:03d}" for i in range(RETAILER_COUNT)]


def retailer_phone(index: int) -> str:
    if not 0 <= index < RETAILER_COUNT:
        raise IndexError(f"retailer index {index} outside 0..{RETAILER_COUNT - 1}")
    return f"{RETAILER_PHONE_PREFIX}{index:03d}"


def _uid(key: str) -> str:
    return str(uuid.uuid5(NAMESPACE, key))


def _connect():
    port = int(
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT")
        or "5432"
    )
    return psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST") or os.environ.get("PGHOST", "127.0.0.1"),
        port=port,
        user=os.environ.get("POL_API_DB_USER") or os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("POL_API_DB_PASSWORD") or os.environ.get("PGPASSWORD"),
        connect_timeout=5,
    )


def _row_id(cur, table: str, where: str, params: tuple) -> str | None:
    cur.execute(f"SELECT id FROM {table} WHERE {where} LIMIT 1;", params)
    row = cur.fetchone()
    return str(row["id"]) if row else None


def _ensure(cur, table: str, values: dict, on_conflict: str = "id") -> str:
    """Insert a row keyed by its deterministic UUID unless it already exists."""
    row_id = str(values["id"])
    if _row_id(cur, table, "id = %s", (row_id,)):
        return row_id
    cols = ", ".join(values)
    placeholders = ", ".join(["%s"] * len(values))
    cur.execute(
        f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) "
        f"ON CONFLICT ({on_conflict}) DO NOTHING;",
        tuple(values.values()),
    )
    if _row_id(cur, table, "id = %s", (row_id,)) is None:
        raise RuntimeError(f"Failed to create row in {table}: {values}")
    return row_id


def seed() -> dict:
    conn = _connect()
    fixture: dict = {"retailer_phones": retailer_phones(), "products": []}
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # ---- shared catalog tree -------------------------------------
            brand_id = _ensure(
                cur,
                "brands",
                {
                    "id": _uid("brand"),
                    "name_fa": "برند آزمایشی پل",
                    "slug": "pol-e2e-brand",
                },
            )
            category_id = _ensure(
                cur,
                "categories",
                {"id": _uid("category"), "name_fa": "کالای اساسی", "slug": "pol-e2e-category"},
            )
            subcategory_id = _ensure(
                cur,
                "subcategories",
                {
                    "id": _uid("subcategory"),
                    "category_id": category_id,
                    "name_fa": "خشکبار و نوشیدنی",
                    "slug": "pol-e2e-subcategory",
                },
            )

            # ---- vendor account ------------------------------------------
            vendor_user_id = _ensure(
                cur,
                "users",
                {
                    "id": _uid("vendor-user"),
                    "phone_number": VENDOR_PHONE,
                    "role": "VENDOR_OWNER",
                    "full_name": "بنکدار آزمایشی",
                },
                on_conflict="phone_number",
            )
            vendor_org_id = _ensure(
                cur,
                "organizations",
                {
                    "id": _uid("vendor-org"),
                    "name": "بنکداری آزمایشی پل",
                    "org_type": "VENDOR",
                    "status": "ACTIVE",
                },
            )
            _ensure(
                cur,
                "organization_memberships",
                {
                    "id": _uid("vendor-membership"),
                    "organization_id": vendor_org_id,
                    "user_id": vendor_user_id,
                    "role": "VENDOR_OWNER",
                    "status": "ACTIVE",
                    "is_primary": True,
                },
            )
            vendor_id = _ensure(
                cur,
                "vendors",
                {
                    "id": _uid("vendor"),
                    "user_id": vendor_user_id,
                    "organization_id": vendor_org_id,
                    "business_name": "بنکداری آزمایشی پل",
                    "warehouse_address": "اهواز، شهرک بنکداران، فاز ۱",
                    "min_order_value_toman": MIN_ORDER_VALUE_TOMAN,
                    "status": "ACTIVE",
                },
            )

            # ---- products + live supply ----------------------------------
            for sku, name in PRODUCTS:
                product_id = _ensure(
                    cur,
                    "products",
                    {
                        "id": _uid(f"product:{sku}"),
                        "master_sku": sku,
                        "canonical_name_fa": name,
                        "brand_id": brand_id,
                        "category_id": category_id,
                        "subcategory_id": subcategory_id,
                        "is_active": True,
                        "is_verified": True,
                    },
                    on_conflict="master_sku",
                )
                vendor_product_id = _ensure(
                    cur,
                    "vendor_products",
                    {
                        "id": _uid(f"vp:{sku}"),
                        "vendor_id": vendor_id,
                        "product_id": product_id,
                        "vendor_sku": f"E2E-{sku}",
                        "packaging_unit": "CARTON",
                        "pack_quantity": PACK_QUANTITY,
                        "listing_status": "ACTIVE",
                        "is_active": True,
                    },
                )

                cur.execute(
                    """
                    UPDATE vendor_inventory
                       SET physical_quantity = %s, reserved_quantity = 0,
                           freshness_status = 'FRESH', updated_at = now()
                     WHERE vendor_product_id = %s;
                    """,
                    (PHYSICAL_QUANTITY, vendor_product_id),
                )
                if not cur.rowcount:
                    cur.execute(
                        """
                        INSERT INTO vendor_inventory
                            (id, vendor_product_id, inventory_unit, physical_quantity,
                             reserved_quantity, moq, freshness_status)
                        VALUES (%s, %s, 'CARTON', %s, 0, 1, 'FRESH');
                        """,
                        (_uid(f"inv:{sku}"), vendor_product_id, PHYSICAL_QUANTITY),
                    )

                cur.execute(
                    "UPDATE vendor_prices SET price_toman = %s, effective_from = now(), "
                    "effective_to = NULL WHERE vendor_product_id = %s AND is_current = TRUE;",
                    (PRICE_TOMAN, vendor_product_id),
                )
                if not cur.rowcount:
                    cur.execute(
                        """
                        INSERT INTO vendor_prices
                            (id, vendor_product_id, price_toman, is_current)
                        VALUES (%s, %s, %s, TRUE);
                        """,
                        (_uid(f"price:{sku}"), vendor_product_id, PRICE_TOMAN),
                    )

                fixture["products"].append(
                    {
                        "product_id": product_id,
                        "master_sku": sku,
                        "name": name,
                        "vendor_product_id": vendor_product_id,
                        "pack_quantity": PACK_QUANTITY,
                        "unit": "CARTON",
                        "price_toman": PRICE_TOMAN,
                    }
                )

            # ---- retailer accounts ---------------------------------------
            for index in range(RETAILER_COUNT):
                phone = retailer_phone(index)
                user_id = _ensure(
                    cur,
                    "users",
                    {
                        "id": _uid(f"retailer-user:{index}"),
                        "phone_number": phone,
                        "role": "RETAILER_OWNER",
                        "full_name": f"خریدار آزمایشی {index:02d}",
                    },
                    on_conflict="phone_number",
                )
                org_id = _ensure(
                    cur,
                    "organizations",
                    {
                        "id": _uid(f"retailer-org:{index}"),
                        "name": f"فروشگاه آزمایشی {index:02d}",
                        "org_type": "RETAILER",
                        "status": "ACTIVE",
                    },
                )
                _ensure(
                    cur,
                    "organization_memberships",
                    {
                        "id": _uid(f"retailer-membership:{index}"),
                        "organization_id": org_id,
                        "user_id": user_id,
                        "role": "RETAILER_OWNER",
                        "status": "ACTIVE",
                        "is_primary": True,
                    },
                )
                _ensure(
                    cur,
                    "retailers",
                    {
                        "id": _uid(f"retailer:{index}"),
                        "user_id": user_id,
                        "organization_id": org_id,
                        "store_name": f"سوپرمارکت آزمایشی {index:02d}",
                        "city": "Ahvaz",
                        "neighborhood": "کیانپارس",
                        "address": f"اهواز، کیانپارس، فاز {index % 4 + 1}، پلاک {index + 1}",
                        "onboarding_status": "ACTIVE_SELF_SERVICE",
                    },
                )

            # ---- clean slate for the seeded tenants ----------------------
            cur.execute(
                """
                UPDATE baskets
                   SET status = 'EXPIRED', updated_at = now()
                 WHERE status = 'OPEN'
                   AND retailer_id IN (
                        SELECT id FROM retailers WHERE user_id IN (
                            SELECT id FROM users WHERE phone_number = ANY(%s)
                        )
                   );
                """,
                (retailer_phones(),),
            )
            fixture["closed_baskets"] = cur.rowcount

            cur.execute(
                "DELETE FROM otp_challenges WHERE phone_number = ANY(%s);",
                (retailer_phones() + [VENDOR_PHONE],),
            )
            fixture["cleared_otp_challenges"] = cur.rowcount

            fixture["vendor_id"] = vendor_id
            fixture["vendor_org_id"] = vendor_org_id
        conn.commit()
    finally:
        conn.close()
    return fixture


if __name__ == "__main__":
    # ensure_ascii: Windows consoles may run a code page that cannot encode
    # the Persian product names in the fixture summary.
    print(json.dumps(seed(), ensure_ascii=True, indent=2))
