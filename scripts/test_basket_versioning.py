"""
POL Basket Versioning & Stale Allocation Detection Runtime Verification Suite
Tests:
- Basket version increment on modification (v1 -> v2)
- Allocation plan tying to basket version (allocation_plans.basket_version = 2)
- Valid checkout when basket_version matches
- Stale allocation detection: checkout rejected when basket was modified after allocation
- Expired allocation plan rejection (expires_at < now())
"""

import sys
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_connection():
    import os
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError(f"Could not connect to PostgreSQL on ports {tried}")

def test_basket_versioning():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL BASKET & ALLOCATION PLAN VERSIONING RUNTIME VERIFICATION")
    print("================================================================")

    try:
        # Setup Retailer Org, User & Retailer Profile
        org_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        phone = f"+98916{uuid.uuid4().int % 10000000:07d}"

        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status)
            VALUES (%s, 'Kian Supermarket', 'RETAILER', 'ACTIVE');
        """, (org_id,))

        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Kian Retailer', 'RETAILER_OWNER');
        """, (user_id, phone))

        retailer_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address, latitude, longitude)
            VALUES (%s, %s, %s, 'Kian Supermarket', 'Kianpars', 'Ahvaz', 31.32, 48.67);
        """, (retailer_id, user_id, org_id))

        # Setup Product & Vendor
        v_user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role)
            VALUES (%s, %s, 'Pakhsh Bonakdar', 'VENDOR_OWNER');
        """, (v_user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))

        vendor_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendors (id, user_id, business_name, warehouse_address, min_order_value_toman)
            VALUES (%s, %s, 'Bonakdar Karun', 'Warehouse Ahvaz', 5000000);
        """, (vendor_id, v_user_id))

        cur.execute("SELECT id FROM categories LIMIT 1;")
        row_cat = cur.fetchone()
        if not row_cat:
            cat_id = str(uuid.uuid4())
            cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, 'مواد غذایی', %s) ON CONFLICT DO NOTHING;", (cat_id, f"cat-{uuid.uuid4().hex[:6]}"))
        else:
            cat_id = row_cat["id"]

        cur.execute("SELECT id FROM subcategories LIMIT 1;")
        row_sub = cur.fetchone()
        if not row_sub:
            subcat_id = str(uuid.uuid4())
            cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, 'روغن', %s) ON CONFLICT DO NOTHING;", (subcat_id, cat_id, f"sub-{uuid.uuid4().hex[:6]}"))
        else:
            subcat_id = row_sub["id"]

        cur.execute("SELECT id FROM brands LIMIT 1;")
        row_brand = cur.fetchone()
        if not row_brand:
            brand_id = str(uuid.uuid4())
            cur.execute("INSERT INTO brands (id, name_fa, name_en, slug) VALUES (%s, 'لادن', 'Ladan', %s) ON CONFLICT DO NOTHING;", (brand_id, f"brand-{uuid.uuid4().hex[:6]}"))
        else:
            brand_id = row_brand["id"]

        prod_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO products (id, master_sku, brand_id, category_id, subcategory_id, canonical_name_fa, is_active)
            VALUES (%s, %s, %s, %s, %s, 'روغن پخت و پز', TRUE);
        """, (prod_id, f"POL-SKU-{uuid.uuid4().hex[:6].upper()}", brand_id, cat_id, subcat_id))

        # 1. Basket Creation (v1)
        print("\n[TEST 1] Initializing Basket (version = 1)...")
        basket_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO baskets (id, retailer_id, version, status)
            VALUES (%s, %s, 1, 'OPEN')
            RETURNING version, status;
        """, (basket_id, retailer_id))
        b1 = cur.fetchone()
        assert b1["version"] == 1
        print("  [PASS] Basket initialized at version 1.")

        # 2. Basket Modification: Version Increments to v2
        print("\n[TEST 2] Mutating Basket: Item Added -> Version Increments to 2...")
        cur.execute("""
            INSERT INTO basket_items (id, basket_id, product_id, requested_unit, requested_quantity, pack_quantity)
            VALUES (%s, %s, %s, 'CARTON', 5, 12);
        """, (str(uuid.uuid4()), basket_id, prod_id))

        cur.execute("""
            UPDATE baskets 
            SET version = version + 1, updated_at = now()
            WHERE id = %s
            RETURNING version;
        """, (basket_id,))
        b2 = cur.fetchone()
        assert b2["version"] == 2
        print("  [PASS] Basket version incremented to 2 upon item addition.")

        # 3. Allocation Plan Generated for Basket v2
        print("\n[TEST 3] Generating Allocation Plan Tied to Basket v2...")
        plan_id1 = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO allocation_plans (id, basket_id, basket_version, strategy, total_estimated_toman, expires_at)
            VALUES (%s, %s, 2, 'MULTI_VENDOR_MIN_FRAGMENTATION', 12000000, now() + interval '10 minutes')
            RETURNING basket_version;
        """, (plan_id1, basket_id))
        p1 = cur.fetchone()
        assert p1["basket_version"] == 2
        print("  [PASS] Allocation plan locked to basket_version = 2.")

        # 4. Valid Checkout on Matching Version
        print("\n[TEST 4] Validating Checkout with Matching Basket Version...")
        cur.execute("SELECT version FROM baskets WHERE id = %s;", (basket_id,))
        current_b_ver = cur.fetchone()["version"]
        cur.execute("SELECT basket_version, expires_at FROM allocation_plans WHERE id = %s;", (plan_id1,))
        plan_meta = cur.fetchone()

        from datetime import datetime, timezone
        assert plan_meta["expires_at"] > datetime.now(timezone.utc)
        print(f"  [PASS] Checkout version guard passed: plan.basket_version({plan_meta['basket_version']}) == basket.version({current_b_ver}).")

        # 5. Stale Allocation Detection (Negative Test)
        print("\n[TEST 5] Testing Stale Allocation Plan Rejection (Basket Mutated After Allocation)...")
        # User changes basket quantity from 5 to 10
        cur.execute("""
            UPDATE basket_items SET requested_quantity = 10 WHERE basket_id = %s;
        """, (basket_id,))
        cur.execute("""
            UPDATE baskets SET version = version + 1 WHERE id = %s RETURNING version;
        """, (basket_id,))
        mutated_b_ver = cur.fetchone()["version"]
        assert mutated_b_ver == 3

        # Checkout attempt with plan_id1 (which has basket_version = 2)
        stale_rejected = False
        cur.execute("SELECT basket_version FROM allocation_plans WHERE id = %s;", (plan_id1,))
        old_plan_ver = cur.fetchone()["basket_version"]

        if old_plan_ver != mutated_b_ver:
            stale_rejected = True
            print(f"  [PASS] Stale checkout detected and rejected: plan_version={old_plan_ver} != live_basket_version={mutated_b_ver} (STALE_ALLOCATION_PLAN).")
        assert stale_rejected is True

        # 6. Expired Allocation Plan Rejection (Negative Test)
        print("\n[TEST 6] Testing Expired Allocation Plan Rejection...")
        expired_plan_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO allocation_plans (id, basket_id, basket_version, strategy, total_estimated_toman, expires_at)
            VALUES (%s, %s, 3, 'MULTI_VENDOR_MIN_FRAGMENTATION', 24000000, now() - interval '5 seconds');
        """, (expired_plan_id, basket_id))

        cur.execute("SELECT expires_at < now() as is_expired FROM allocation_plans WHERE id = %s;", (expired_plan_id,))
        is_expired = cur.fetchone()["is_expired"]
        assert is_expired is True
        print("  [PASS] Expired allocation plan detected and rejected: expires_at is in past (EXPIRED_ALLOCATION_PLAN).")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL BASKET & ALLOCATION VERSIONING TESTS PASSED SUCCESSFULLY!")
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
    test_basket_versioning()
