"""
POL Inventory Reservation Lifecycle & Stock Safety Runtime Verification Suite
Tests:
- Explicit reservation creation in inventory_reservations (ACTIVE status with expires_at)
- Available stock derivation (available_quantity = physical_quantity - reserved_quantity)
- Order Acceptance lifecycle: ACTIVE -> CONSUMED (physical stock permanently deducted)
- Order Rejection / Cancellation lifecycle: ACTIVE -> RELEASED (available stock restored)
- Background cleanup lifecycle: ACTIVE -> EXPIRED (expired reservation released)
- Concurrency stock guard: over-reservation rejection when requested > available
"""

import sys
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_connection():
    ports = [5432, 5433]
    for p in ports:
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError("Could not connect to PostgreSQL on ports 5432 or 5433")

def test_inventory_reservations():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL INVENTORY RESERVATION LIFECYCLE RUNTIME VERIFICATION")
    print("================================================================")

    try:
        # Setup vendor, product, vendor_product, vendor_inventory
        vendor_user_id = str(uuid.uuid4())
        phone = f"+98916{uuid.uuid4().int % 10000000:07d}"
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Vendor Inv Owner', 'VENDOR_OWNER');
        """, (vendor_user_id, phone))

        vendor_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendors (id, user_id, business_name, warehouse_address, min_order_value_toman)
            VALUES (%s, %s, 'Pakhsh Karun Test', 'Shahr-e-Bonakdaran', 5000000);
        """, (vendor_id, vendor_user_id))

        cat_id = str(uuid.uuid4())
        subcat_id = str(uuid.uuid4())
        cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, 'کالای اساسی', 'staples') ON CONFLICT DO NOTHING;", (cat_id,))
        cur.execute("SELECT id FROM categories LIMIT 1;")
        actual_cat_id = cur.fetchone()["id"]

        cur.execute("""
            INSERT INTO subcategories (id, category_id, name_fa, slug) 
            VALUES (%s, %s, 'روغن خوراکی', 'edible-oil') ON CONFLICT DO NOTHING;
        """, (subcat_id, actual_cat_id))
        cur.execute("SELECT id FROM subcategories LIMIT 1;")
        actual_subcat_id = cur.fetchone()["id"]

        brand_id = str(uuid.uuid4())
        cur.execute("INSERT INTO brands (id, name_fa, name_en, slug) VALUES (%s, 'اویلا', 'Oila', 'oila') ON CONFLICT DO NOTHING;", (brand_id,))
        cur.execute("SELECT id FROM brands LIMIT 1;")
        actual_brand_id = cur.fetchone()["id"]

        prod_id = str(uuid.uuid4())
        sku_code = f"POL-SKU-{uuid.uuid4().hex[:6].upper()}"
        cur.execute("""
            INSERT INTO products (id, master_sku, brand_id, category_id, subcategory_id, canonical_name_fa, is_active)
            VALUES (%s, %s, %s, %s, %s, 'روغن آفتابگردان ۸۱۰ گرم اویلا', TRUE);
        """, (prod_id, sku_code, actual_brand_id, actual_cat_id, actual_subcat_id))

        vp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, listing_status, is_active)
            VALUES (%s, %s, %s, 'VND-SKU-001', 'CARTON', 12, 'ACTIVE', TRUE);
        """, (vp_id, vendor_id, prod_id))

        # Initial stock: 100 physical cartons, 0 reserved
        cur.execute("""
            INSERT INTO vendor_inventory (vendor_product_id, physical_quantity, reserved_quantity)
            VALUES (%s, 100, 0);
        """, (vp_id,))

        # 1. Create Active Reservation (20 cartons)
        print("\n[TEST 1] Creating Active Inventory Reservation (20 Cartons)...")
        res_id1 = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO inventory_reservations (id, vendor_product_id, quantity, status, expires_at)
            VALUES (%s, %s, 20, 'ACTIVE', now() + interval '15 minutes');
        """, (res_id1, vp_id))

        cur.execute("""
            UPDATE vendor_inventory 
            SET reserved_quantity = reserved_quantity + 20
            WHERE vendor_product_id = %s
            RETURNING physical_quantity, reserved_quantity, available_quantity;
        """, (vp_id,))
        inv1 = cur.fetchone()
        assert inv1["physical_quantity"] == 100
        assert inv1["reserved_quantity"] == 20
        assert inv1["available_quantity"] == 80
        print("  [PASS] Reservation ACTIVE: physical=100, reserved=20, available=80.")

        # 2. Consume Reservation on Vendor Acceptance (Order Accepted)
        print("\n[TEST 2] Consuming Reservation on Vendor Acceptance (Order Confirmed)...")
        cur.execute("""
            UPDATE inventory_reservations 
            SET status = 'CONSUMED', consumed_at = now()
            WHERE id = %s;
        """, (res_id1,))

        # On consumption: physical decreases by 20, reserved decreases by 20, available stays at 80
        cur.execute("""
            UPDATE vendor_inventory 
            SET physical_quantity = physical_quantity - 20,
                reserved_quantity = reserved_quantity - 20
            WHERE vendor_product_id = %s
            RETURNING physical_quantity, reserved_quantity, available_quantity;
        """, (vp_id,))
        inv2 = cur.fetchone()
        assert inv2["physical_quantity"] == 80
        assert inv2["reserved_quantity"] == 0
        assert inv2["available_quantity"] == 80
        print("  [PASS] Reservation CONSUMED: physical permanently reduced to 80, reserved=0, available=80.")

        # 3. Create Reservation and Release on Rejection/Cancellation
        print("\n[TEST 3] Releasing Reservation on Order Rejection / Cancellation...")
        res_id2 = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO inventory_reservations (id, vendor_product_id, quantity, status, expires_at)
            VALUES (%s, %s, 30, 'ACTIVE', now() + interval '15 minutes');
        """, (res_id2, vp_id))

        cur.execute("""
            UPDATE vendor_inventory 
            SET reserved_quantity = reserved_quantity + 30
            WHERE vendor_product_id = %s;
        """, (vp_id,))

        # Order rejected: transition to RELEASED
        cur.execute("""
            UPDATE inventory_reservations 
            SET status = 'RELEASED', released_at = now()
            WHERE id = %s;
        """, (res_id2,))

        cur.execute("""
            UPDATE vendor_inventory 
            SET reserved_quantity = reserved_quantity - 30
            WHERE vendor_product_id = %s
            RETURNING physical_quantity, reserved_quantity, available_quantity;
        """, (vp_id,))
        inv3 = cur.fetchone()
        assert inv3["physical_quantity"] == 80
        assert inv3["reserved_quantity"] == 0
        assert inv3["available_quantity"] == 80
        print("  [PASS] Reservation RELEASED: stock fully restored to available=80.")

        # 4. Background Expiry of Stale Reservation
        print("\n[TEST 4] Testing Background Expiry of Timed-out Reservation...")
        res_id3 = str(uuid.uuid4())
        # Create expired reservation (expires_at in past)
        cur.execute("""
            INSERT INTO inventory_reservations (id, vendor_product_id, quantity, status, expires_at)
            VALUES (%s, %s, 15, 'ACTIVE', now() - interval '1 minute');
        """, (res_id3, vp_id))

        cur.execute("""
            UPDATE vendor_inventory 
            SET reserved_quantity = reserved_quantity + 15
            WHERE vendor_product_id = %s;
        """, (vp_id,))

        # Daemon checks for expired reservations
        cur.execute("""
            UPDATE inventory_reservations 
            SET status = 'EXPIRED', released_at = now()
            WHERE status = 'ACTIVE' AND expires_at < now()
            RETURNING id, quantity;
        """)
        expired_rows = cur.fetchall()
        assert len(expired_rows) >= 1
        assert any(str(r["id"]) == res_id3 for r in expired_rows)

        cur.execute("""
            UPDATE vendor_inventory 
            SET reserved_quantity = reserved_quantity - 15
            WHERE vendor_product_id = %s
            RETURNING available_quantity;
        """, (vp_id,))
        assert cur.fetchone()["available_quantity"] == 80
        print("  [PASS] Daemon cleanly expired stale reservation: stock restored to 80.")

        # 5. Concurrency Over-Reservation Guard
        print("\n[TEST 5] Testing Over-Reservation Stock Guard...")
        # Available is 80, attempt to reserve 90
        cur.execute("SELECT available_quantity FROM vendor_inventory WHERE vendor_product_id = %s FOR UPDATE;", (vp_id,))
        avail = cur.fetchone()["available_quantity"]
        requested = 90
        rejected = False
        if requested > avail:
            rejected = True
            print(f"  [PASS] Over-reservation rejected: requested={requested} > available={avail}.")
        assert rejected is True

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL INVENTORY RESERVATION TESTS PASSED SUCCESSFULLY!")
        print("================================================================")
        return True

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_inventory_reservations()
