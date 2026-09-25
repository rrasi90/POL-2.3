import uuid
from datetime import timedelta

import psycopg2
from psycopg2.extras import RealDictCursor

from scripts.reservation_expiry_worker import ReservationExpiryWorker


def _db():
    return psycopg2.connect(
        dbname="pol_test",
        user="postgres",
        host="127.0.0.1",
        port=5432,
        cursor_factory=RealDictCursor,
    )


def test_reservation_expiry_releases_inventory_and_is_idempotent():
    conn = _db()
    try:
        with conn:
            with conn.cursor() as cur:
                user_id = str(uuid.uuid4())
                org_id = str(uuid.uuid4())
                vendor_id = str(uuid.uuid4())
                product_id = str(uuid.uuid4())
                vp_id = str(uuid.uuid4())
                res_id = str(uuid.uuid4())

                cur.execute(
                    "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,'Expiry Vendor','VENDOR_OWNER')",
                    (user_id, f"+9891{uuid.uuid4().int % 100000000:08d}"),
                )
                cur.execute(
                    "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'Expiry Vendor Org','VENDOR','ACTIVE')",
                    (org_id,),
                )
                cur.execute(
                    """
                    INSERT INTO organization_memberships
                        (id,organization_id,user_id,role,status)
                    VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE')
                    """,
                    (str(uuid.uuid4()), org_id, user_id),
                )
                cur.execute(
                    """
                    INSERT INTO vendors
                        (id,user_id,organization_id,business_name,warehouse_address,min_order_value_toman,status)
                    VALUES (%s,%s,%s,'Expiry Vendor','Ahvaz',1000000,'ACTIVE')
                    """,
                    (vendor_id, user_id, org_id),
                )
                brand_id = str(uuid.uuid4())
                category_id = str(uuid.uuid4())
                subcategory_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO brands (id,name_fa,slug)
                    VALUES (%s,'Expiry Brand',%s)
                    """,
                    (brand_id, f"expiry-brand-{uuid.uuid4().hex[:8]}"),
                )
                cur.execute(
                    """
                    INSERT INTO categories (id,name_fa,slug)
                    VALUES (%s,'Expiry Category',%s)
                    """,
                    (category_id, f"expiry-category-{uuid.uuid4().hex[:8]}"),
                )
                cur.execute(
                    """
                    INSERT INTO subcategories (id,category_id,name_fa,slug)
                    VALUES (%s,%s,'Expiry Subcategory',%s)
                    """,
                    (subcategory_id, category_id, f"expiry-subcategory-{uuid.uuid4().hex[:8]}"),
                )
                cur.execute(
                    """
                    INSERT INTO products
                        (id,master_sku,canonical_name_fa,brand_id,category_id,subcategory_id,is_active)
                    VALUES (%s,%s,'Expiry Test Product',%s,%s,%s,TRUE)
                    """,
                    (product_id, f"EXP-{uuid.uuid4().hex[:10]}", brand_id, category_id, subcategory_id),
                )
                cur.execute(
                    """
                    INSERT INTO vendor_products
                        (id,vendor_id,product_id,vendor_sku,packaging_unit,pack_quantity,listing_status,is_active)
                    VALUES (%s,%s,%s,%s,'CARTON',12,'ACTIVE',TRUE)
                    """,
                    (vp_id, vendor_id, product_id, f"EXP-VP-{uuid.uuid4().hex[:8]}"),
                )
                cur.execute(
                    """
                    INSERT INTO vendor_inventory
                        (vendor_product_id,physical_quantity,reserved_quantity)
                    VALUES (%s,100,20)
                    """,
                    (vp_id,),
                )
                cur.execute(
                    """
                    INSERT INTO inventory_reservations
                        (id,vendor_product_id,quantity,status,idempotency_key,expires_at)
                    VALUES (%s,%s,20,'ACTIVE',%s,now()-interval '1 minute')
                    """,
                    (res_id, vp_id, f"expiry-{uuid.uuid4()}"),
                )

                result = ReservationExpiryWorker.process_expired(
                    cur,
                    now=None,
                    limit=10,
                )
                assert result["expired_reservation_count"] == 1
                assert result["released_quantity"] == 20

                cur.execute(
                    "SELECT reserved_quantity FROM vendor_inventory WHERE vendor_product_id=%s",
                    (vp_id,),
                )
                assert cur.fetchone()["reserved_quantity"] == 0

                cur.execute(
                    "SELECT status FROM inventory_reservations WHERE id=%s",
                    (res_id,),
                )
                assert cur.fetchone()["status"] == "EXPIRED"

                cur.execute(
                    """
                    SELECT old_reserved_quantity,new_reserved_quantity,source_trigger
                    FROM inventory_audit_log
                    WHERE reference_id=%s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (res_id,),
                )
                audit = cur.fetchone()
                assert audit["old_reserved_quantity"] == 20
                assert audit["new_reserved_quantity"] == 0
                assert audit["source_trigger"] == "RESERVATION_EXPIRY"

                again = ReservationExpiryWorker.process_expired(cur, limit=10)
                assert again["expired_reservation_count"] == 0
    finally:
        conn.close()
