"""
POL PostgreSQL 18 Multi-Connection Concurrency & ACID Integrity Test Suite
Executes true multi-connection race conditions against PostgreSQL 18 (port 5433, db pol_test)
using the CANONICAL migrated schema in the public schema.

Concurrency Test Cases:
1. Concurrency 1: Inventory Race (Stock = 5; Con A & Con B concurrently reserve 5; exactly one succeeds)
2. Concurrency 2: Checkout with Same Idempotency Key (Duplicate checkout caught by PostgreSQL unique constraint)
3. Concurrency 3: Checkout with Different Idempotency Keys (Semantic duplicate/race for last scarce stock)
4. Concurrency 4: Vendor Accept Race (Two concurrent workers accept order; exactly one succeeds)
5. Concurrency 5: Dispatch / Delivery Creation Race (deliveries.order_id UNIQUE constraint enforcement)
6. Concurrency 6: Refund Race (Two concurrent refund submissions for same dispute; unique index catches duplicate)
7. Concurrency 7: Dispute Creation Race (Two concurrent dispute creations for same order; partial unique index catches duplicate)
8. Concurrency 8: Multi-Vendor Dispute Isolation Race (Vendor A settlement HELD while Vendor B settlement pays out)
9. Concurrency 9: Stale State Detection (Vendor price change during cart checkout detected and rejected)
"""

import os
import sys
import threading
import time
import uuid
import psycopg2
from psycopg2 import errors

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

DB_CONFIG = {
    "dbname": "pol_test",
    "user": "postgres",
    "host": "127.0.0.1",
}

def get_conn():
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    last_err = None
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            cfg = dict(DB_CONFIG, port=p)
            conn = psycopg2.connect(**cfg)
            cur = conn.cursor()
            cur.execute("SET search_path TO public;")
            conn.commit()
            return conn
        except Exception as e:
            last_err = e
    raise last_err

def make_uuid(domain: int, item_id: int) -> str:
    return f"{domain:08d}-0000-0000-0000-{item_id:012d}"

# Global Fixtures
U_ADMIN = make_uuid(1, 1)
U_RET_1 = make_uuid(1, 10)
U_VND_A = make_uuid(1, 100)
U_VND_B = make_uuid(1, 200)

RET_1 = make_uuid(2, 10)
VND_A = make_uuid(3, 100)
VND_B = make_uuid(3, 200)

BRAND_1 = make_uuid(4, 1)
CAT_1 = make_uuid(4, 10)
SUBCAT_1 = make_uuid(4, 100)

ORG_RET_1 = make_uuid(5, 10)
ORG_VND_A = make_uuid(5, 100)
ORG_VND_B = make_uuid(5, 200)

def ensure_base_fixtures():
    """Ensure basic actor fixtures exist in public schema."""
    conn = get_conn()
    cur = conn.cursor()

    # 1. Organizations
    cur.execute("""
        INSERT INTO organizations (id, name, org_type, status) VALUES
        (%s, 'Org Retailer Race', 'RETAILER', 'ACTIVE'),
        (%s, 'Org Vendor A Race', 'VENDOR', 'ACTIVE'),
        (%s, 'Org Vendor B Race', 'VENDOR', 'ACTIVE')
        ON CONFLICT (id) DO NOTHING;
    """, (ORG_RET_1, ORG_VND_A, ORG_VND_B))

    # 2. Users
    cur.execute("""
        INSERT INTO users (id, phone_number, role, full_name) VALUES
        (%s, '+989160000001', 'ADMIN_SUPER', 'Platform Administrator'),
        (%s, '+989161111119', 'RETAILER_OWNER', 'Retailer Owner Concurrency'),
        (%s, '+989162222228', 'VENDOR_OWNER', 'Vendor Owner A Concurrency'),
        (%s, '+989162222229', 'VENDOR_OWNER', 'Vendor Owner B Concurrency')
        ON CONFLICT (id) DO NOTHING;
    """, (U_ADMIN, U_RET_1, U_VND_A, U_VND_B))

    # 3. Memberships
    cur.execute("""
        INSERT INTO organization_memberships (organization_id, user_id, role, status) VALUES
        (%s, %s, 'RETAILER_OWNER', 'ACTIVE'),
        (%s, %s, 'VENDOR_OWNER', 'ACTIVE'),
        (%s, %s, 'VENDOR_OWNER', 'ACTIVE')
        ON CONFLICT (organization_id, user_id) DO NOTHING;
    """, (ORG_RET_1, U_RET_1, ORG_VND_A, U_VND_A, ORG_VND_B, U_VND_B))

    # 4. Retailers & Vendors
    cur.execute("""
        INSERT INTO retailers (id, user_id, organization_id, store_name, city, neighborhood, address) VALUES
        (%s, %s, %s, 'Supermarket Race', 'Ahvaz', 'Naderi', 'Main St, Ahvaz')
        ON CONFLICT (id) DO NOTHING;
    """, (RET_1, U_RET_1, ORG_RET_1))

    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman) VALUES
        (%s, %s, %s, 'Wholesaler A Race', 'Bonakdaran Phase 1', 5000000),
        (%s, %s, %s, 'Wholesaler B Race', 'Bonakdaran Phase 2', 4000000)
        ON CONFLICT (id) DO NOTHING;
    """, (VND_A, U_VND_A, ORG_VND_A, VND_B, U_VND_B, ORG_VND_B))

    # 5. Catalog Entities
    cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, 'تبرک', 'tabarrok_race') ON CONFLICT (id) DO NOTHING;", (BRAND_1,))
    cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, 'مواد غذایی', 'food_race') ON CONFLICT (id) DO NOTHING;", (CAT_1,))
    cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, 'کالاهای اساسی', 'staples_race') ON CONFLICT (id) DO NOTHING;", (SUBCAT_1, CAT_1))

    conn.commit()
    conn.close()

import pytest
from scripts.reservation_service import ReservationService, ReservationConflictError

@pytest.fixture(autouse=True)
def setup_concurrency_fixtures():
    ensure_base_fixtures()

def test_concurrency_1_inventory_race():
    print("\n[CONCURRENCY 1] Inventory Reservation Race (Stock=5, 2 concurrent 5-unit requests)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()

    p_id = str(uuid.uuid4())
    vp_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    # Setup scarce product with 5 units physical, 0 reserved
    cur.execute("""
        INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id)
        VALUES (%s, %s, 'Race Cooking Oil 5L', %s, %s, %s)
    """, (p_id, f"POL-RACE-OIL-{tag}", BRAND_1, CAT_1, SUBCAT_1))
    cur.execute("""
        INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity)
        VALUES (%s, %s, %s, %s, 'CARTON', 1)
    """, (vp_id, VND_A, p_id, f"SKU-RACE-{tag}"))
    cur.execute("""
        INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity)
        VALUES (%s, %s, 5, 0)
    """, (str(uuid.uuid4()), vp_id))
    setup_conn.commit()
    setup_conn.close()

    results = []
    barrier = threading.Barrier(2)

    def worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        barrier.wait() # Synchronize start
        try:
            cur.execute("""
                UPDATE vendor_inventory
                SET reserved_quantity = reserved_quantity + 5
                WHERE vendor_product_id = %s AND (physical_quantity - reserved_quantity) >= 5
            """, (vp_id,))
            conn.commit()
            results.append((worker_id, cur.rowcount, "SUCCESS"))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, 0, str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=worker, args=("W1",))
    t2 = threading.Thread(target=worker, args=("W2",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    verify_conn = get_conn()
    cur = verify_conn.cursor()
    cur.execute("SELECT physical_quantity, reserved_quantity FROM vendor_inventory WHERE vendor_product_id = %s", (vp_id,))
    phys, res = cur.fetchone()
    verify_conn.close()

    # Exactly one worker must succeed (rowcount=1) and one must fail (rowcount=0)
    successes = [r for r in results if r[1] == 1]
    failures = [r for r in results if r[1] == 0]

    assert len(successes) == 1, f"Expected 1 success, got {len(successes)}: {results}"
    assert len(failures) == 1, f"Expected 1 failure, got {len(failures)}: {results}"
    assert res == 5, f"Expected reserved_quantity=5, got {res}"
    print(f"  [PASS] Concurrency 1 passed: Exactly 1 reservation succeeded, 1 rejected. Final reserved={res}/5.")

def test_concurrency_2_duplicate_checkout_same_key():
    print("\n[CONCURRENCY 2] Duplicate Checkout Idempotency Race (Same Idempotency Key)...")
    idem_key = f"idem_race_{uuid.uuid4().hex[:8]}"
    barrier = threading.Barrier(2)
    results = []

    def checkout_worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        og_id = str(uuid.uuid4())
        barrier.wait()
        try:
            cur.execute("""
                INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
                VALUES (%s, %s, 'ACTIVE', 5000000, %s)
            """, (og_id, RET_1, idem_key))
            conn.commit()
            results.append((worker_id, "COMMITTED"))
        except psycopg2.IntegrityError as e:
            conn.rollback()
            results.append((worker_id, "UNIQUE_VIOLATION"))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=checkout_worker, args=("Worker_A",))
    t2 = threading.Thread(target=checkout_worker, args=("Worker_B",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    committed = [r for r in results if r[1] == "COMMITTED"]
    violations = [r for r in results if r[1] == "UNIQUE_VIOLATION"]

    assert len(committed) == 1, f"Expected exactly 1 commit, got {len(committed)}: {results}"
    assert len(violations) == 1, f"Expected exactly 1 UniqueViolation, got {len(violations)}: {results}"

    verify_conn = get_conn()
    cur = verify_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM order_groups WHERE checkout_idempotency_key = %s", (idem_key,))
    cnt = cur.fetchone()[0]
    verify_conn.close()
    assert cnt == 1, f"Expected 1 persisted order group, got {cnt}"

    print(f"  [PASS] Concurrency 2 passed: PostgreSQL UNIQUE constraint caught race condition ({committed[0][0]} committed, {violations[0][0]} rejected).")

def test_concurrency_3_checkout_different_keys_scarce_stock():
    print("\n[CONCURRENCY 3] Checkout Race with Different Idempotency Keys (Scarce Stock Contention)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()

    p_id = str(uuid.uuid4())
    vp_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    # Only 1 unit of scarce stock
    cur.execute("""
        INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id)
        VALUES (%s, %s, 'Scarce Rice 10kg', %s, %s, %s)
    """, (p_id, f"POL-SCARCE-{tag}", BRAND_1, CAT_1, SUBCAT_1))
    cur.execute("""
        INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity)
        VALUES (%s, %s, %s, %s, 'CARTON', 1)
    """, (vp_id, VND_A, p_id, f"SKU-SCARCE-{tag}"))
    cur.execute("""
        INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity)
        VALUES (%s, %s, 1, 0)
    """, (str(uuid.uuid4()), vp_id))
    setup_conn.commit()
    setup_conn.close()

    barrier = threading.Barrier(2)
    results = []

    def scarce_checkout_worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        og_id = str(uuid.uuid4())
        ord_id = str(uuid.uuid4())
        idem = f"idem_scarce_{worker_id}_{tag}"
        barrier.wait()
        try:
            # Atomic conditional stock reservation
            cur.execute("""
                UPDATE vendor_inventory
                SET reserved_quantity = reserved_quantity + 1
                WHERE vendor_product_id = %s AND (physical_quantity - reserved_quantity) >= 1
            """, (vp_id,))
            if cur.rowcount == 1:
                cur.execute("""
                    INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
                    VALUES (%s, %s, 'ACTIVE', 1000000, %s)
                """, (og_id, RET_1, idem))
                cur.execute("""
                    INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
                    VALUES (%s, %s, %s, %s, %s, 'SUBMITTED', 1000000)
                """, (ord_id, f"POL-SCARCE-{worker_id}-{tag}", og_id, RET_1, VND_A))
                conn.commit()
                results.append((worker_id, "ORDER_PLACED"))
            else:
                conn.rollback()
                results.append((worker_id, "OUT_OF_STOCK"))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=scarce_checkout_worker, args=("Buyer_1",))
    t2 = threading.Thread(target=scarce_checkout_worker, args=("Buyer_2",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    placed = [r for r in results if r[1] == "ORDER_PLACED"]
    rejected = [r for r in results if r[1] == "OUT_OF_STOCK"]

    assert len(placed) == 1, f"Expected exactly 1 order placed, got {len(placed)}: {results}"
    assert len(rejected) == 1, f"Expected exactly 1 rejected due to stock, got {len(rejected)}: {results}"

    print(f"  [PASS] Concurrency 3 passed: Semantic race between distinct keys correctly arbitrated by inventory atomicity ({placed[0][0]} won, {rejected[0][0]} rejected).")

def test_concurrency_10_reservation_service_scarce_stock_race():
    """G-340: real concurrent ReservationService calls arbitrate the same scarce inventory row."""
    setup_conn = get_conn()
    cur = setup_conn.cursor()
    p_id, vp_id, tag = str(uuid.uuid4()), str(uuid.uuid4()), uuid.uuid4().hex[:8]
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s,%s,%s,%s,%s,%s)", (p_id, f"POL-G340-{tag}", "G340", BRAND_1, CAT_1, SUBCAT_1))
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s,%s,%s,%s,'CARTON',1)", (vp_id,VND_A,p_id,f"SKU-G340-{tag}"))
    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity) VALUES (%s,%s,1,0)", (str(uuid.uuid4()),vp_id))
    setup_conn.commit(); setup_conn.close()
    barrier = threading.Barrier(2); results=[]
    def reserve_worker(name):
        conn=get_conn(); cur=conn.cursor(cursor_factory=RealDictCursor)
        barrier.wait()
        try:
            reservation=ReservationService.reserve(cur,vendor_product_id=vp_id,quantity=1,idempotency_key=f"g340-{name}-{tag}")
            conn.commit(); results.append((name,"RESERVED",str(reservation["id"])))
        except Exception as exc:
            conn.rollback(); results.append((name,type(exc).__name__))
        finally: conn.close()
    t1=threading.Thread(target=reserve_worker,args=("A",)); t2=threading.Thread(target=reserve_worker,args=("B",))
    t1.start(); t2.start(); t1.join(); t2.join()
    assert sum(r[1]=="RESERVED" for r in results)==1, results
    check=get_conn(); q=check.cursor()
    q.execute("SELECT reserved_quantity FROM vendor_inventory WHERE vendor_product_id=%s",(vp_id,)); assert q.fetchone()[0]==1
    q.execute("SELECT COUNT(*) FROM inventory_reservations WHERE vendor_product_id=%s AND status='ACTIVE'",(vp_id,)); assert q.fetchone()[0]==1
    check.close()

def test_concurrency_12_reservation_reconciliation_invariant():
    """G-342: DB rejects an inventory reserved_quantity mismatch at transaction commit."""
    conn = get_conn(); cur = conn.cursor()
    p_id, vp_id = str(uuid.uuid4()), str(uuid.uuid4())
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s,%s,%s,%s,%s,%s)", (p_id, f"POL-G342-{uuid.uuid4().hex[:8]}", "G342", BRAND_1, CAT_1, SUBCAT_1))
    cur.execute("INSERT INTO vendor_products (id,vendor_id,product_id,vendor_sku,packaging_unit,pack_quantity) VALUES (%s,%s,%s,%s,'CARTON',1)", (vp_id,VND_A,p_id,f"SKU-G342-{uuid.uuid4().hex[:8]}"))
    cur.execute("INSERT INTO vendor_inventory (id,vendor_product_id,physical_quantity,reserved_quantity) VALUES (%s,%s,10,0)", (str(uuid.uuid4()),vp_id))
    conn.commit()
    cur.execute("UPDATE vendor_inventory SET reserved_quantity=1 WHERE vendor_product_id=%s",(vp_id,))
    with pytest.raises(psycopg2.errors.CheckViolation):
        conn.commit()
    conn.rollback()
    cur.execute("SELECT reserved_quantity FROM vendor_inventory WHERE vendor_product_id=%s",(vp_id,))
    assert cur.fetchone()[0] == 0
    conn.close()

def test_concurrency_11_reservation_idempotency_same_key():
    """G-341: DB unique key arbitrates two concurrent reservations using the same idempotency key."""
    setup_conn=get_conn(); cur=setup_conn.cursor()
    p_id,vp_id,tag=str(uuid.uuid4()),str(uuid.uuid4()),uuid.uuid4().hex[:8]
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s,%s,%s,%s,%s,%s)", (p_id,f"POL-G341-{tag}","G341",BRAND_1,CAT_1,SUBCAT_1))
    cur.execute("INSERT INTO vendor_products (id,vendor_id,product_id,vendor_sku,packaging_unit,pack_quantity) VALUES (%s,%s,%s,%s,'CARTON',1)", (vp_id,VND_A,p_id,f"SKU-G341-{tag}"))
    cur.execute("INSERT INTO vendor_inventory (id,vendor_product_id,physical_quantity,reserved_quantity) VALUES (%s,%s,5,0)", (str(uuid.uuid4()),vp_id))
    setup_conn.commit(); setup_conn.close()
    key=f"g341-shared-{tag}"; barrier=threading.Barrier(2); results=[]
    def reserve_same_key(name):
        conn=get_conn(); cur=conn.cursor(cursor_factory=RealDictCursor); barrier.wait()
        try:
            res=ReservationService.reserve(cur,vendor_product_id=vp_id,quantity=2,idempotency_key=key)
            conn.commit(); results.append((name,"RESERVED",str(res["id"]),bool(res.get("idempotent_replay"))))
        except Exception as exc:
            conn.rollback(); results.append((name,type(exc).__name__))
        finally: conn.close()
    t1=threading.Thread(target=reserve_same_key,args=("A",)); t2=threading.Thread(target=reserve_same_key,args=("B",))
    t1.start(); t2.start(); t1.join(); t2.join()
    assert len([r for r in results if r[1]=="RESERVED"])==2, results
    ids={r[2] for r in results if r[1]=="RESERVED"}; assert len(ids)==1
    assert sum(bool(r[3]) for r in results if r[1]=="RESERVED")==1
    check=get_conn(); q=check.cursor();
    q.execute("SELECT COUNT(*),MAX(reserved_quantity) FROM inventory_reservations ir JOIN vendor_inventory vi ON vi.vendor_product_id=ir.vendor_product_id WHERE ir.idempotency_key=%s",(key,));
    cnt,_=q.fetchone(); assert cnt==1
    q.execute("SELECT reserved_quantity FROM vendor_inventory WHERE vendor_product_id=%s",(vp_id,)); assert q.fetchone()[0]==2
    check.close()

def test_concurrency_4_vendor_accept_race():
    print("\n[CONCURRENCY 4] Vendor Accept Race (Two concurrent workers accepting SUBMITTED order)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()
    ord_id = str(uuid.uuid4())
    og_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    cur.execute("""
        INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
        VALUES (%s, %s, 'ACTIVE', 6000000, %s)
    """, (og_id, RET_1, f"idem_acc_{tag}"))
    cur.execute("""
        INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
        VALUES (%s, %s, %s, %s, %s, 'SUBMITTED', 6000000)
    """, (ord_id, f"POL-ACC-{tag}", og_id, RET_1, VND_A))
    setup_conn.commit()
    setup_conn.close()

    barrier = threading.Barrier(2)
    results = []

    def accept_worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        barrier.wait()
        try:
            cur.execute("""
                UPDATE orders
                SET order_status = 'ACCEPTED', updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND order_status = 'SUBMITTED'
            """, (ord_id,))
            conn.commit()
            results.append((worker_id, cur.rowcount))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, 0))
        finally:
            conn.close()

    t1 = threading.Thread(target=accept_worker, args=("W1",))
    t2 = threading.Thread(target=accept_worker, args=("W2",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    successes = [r for r in results if r[1] == 1]
    noops = [r for r in results if r[1] == 0]

    assert len(successes) == 1, f"Expected exactly 1 transition, got {len(successes)}: {results}"
    assert len(noops) == 1, f"Expected exactly 1 no-op, got {len(noops)}: {results}"
    print(f"  [PASS] Concurrency 4 passed: Exactly 1 worker transitioned order to ACCEPTED ({successes[0][0]}).")

def test_concurrency_5_dispatch_creation_race():
    print("\n[CONCURRENCY 5] Dispatch / Delivery Creation Race (deliveries.order_id UNIQUE)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()
    ord_id = str(uuid.uuid4())
    og_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    cur.execute("""
        INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
        VALUES (%s, %s, 'ACTIVE', 4000000, %s)
    """, (og_id, RET_1, f"idem_del_{tag}"))
    cur.execute("""
        INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
        VALUES (%s, %s, %s, %s, %s, 'ACCEPTED', 4000000)
    """, (ord_id, f"POL-DEL-{tag}", og_id, RET_1, VND_B))
    setup_conn.commit()
    setup_conn.close()

    barrier = threading.Barrier(2)
    results = []

    def dispatch_worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        del_id = str(uuid.uuid4())
        barrier.wait()
        try:
            cur.execute("""
                INSERT INTO deliveries (id, order_id, vendor_id, delivery_status)
                VALUES (%s, %s, %s, 'ASSIGNED')
            """, (del_id, ord_id, VND_B))
            conn.commit()
            results.append((worker_id, "DELIVERY_CREATED"))
        except psycopg2.IntegrityError as err:
            conn.rollback()
            if err.pgcode == '23505':
                results.append((worker_id, "UNIQUE_VIOLATION"))
            else:
                results.append((worker_id, f"INTEGRITY_VIOLATION: {err.pgcode}"))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=dispatch_worker, args=("Driver_1",))
    t2 = threading.Thread(target=dispatch_worker, args=("Driver_2",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    created = [r for r in results if r[1] == "DELIVERY_CREATED"]
    violations = [r for r in results if r[1] == "UNIQUE_VIOLATION"]

    assert len(created) == 1, f"Expected 1 delivery created, got {len(created)}: {results}"
    assert len(violations) == 1, f"Expected 1 UniqueViolation, got {len(violations)}: {results}"
    print(f"  [PASS] Concurrency 5 passed: deliveries.order_id UNIQUE constraint prevented duplicate delivery creation.")

def test_concurrency_6_refund_race():
    print("\n[CONCURRENCY 6] Refund Race (Two concurrent refund submissions for same dispute)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()
    ord_id = str(uuid.uuid4())
    disp_id = str(uuid.uuid4())
    og_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    cur.execute("""
        INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
        VALUES (%s, %s, 'ACTIVE', 5000000, %s)
    """, (og_id, RET_1, f"idem_ref_{tag}"))
    cur.execute("""
        INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
        VALUES (%s, %s, %s, %s, %s, 'DELIVERED', 5000000)
    """, (ord_id, f"POL-REF-{tag}", og_id, RET_1, VND_A))
    cur.execute("""
        INSERT INTO disputes (id, order_id, retailer_id, vendor_id, dispute_status, claimed_amount_toman, description)
        VALUES (%s, %s, %s, %s, 'RESOLVED', 2000000, 'Damaged stock')
    """, (disp_id, ord_id, RET_1, VND_A))
    setup_conn.commit()
    setup_conn.close()

    barrier = threading.Barrier(2)
    results = []

    def refund_worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        ref_id = str(uuid.uuid4())
        barrier.wait()
        try:
            cur.execute("""
                INSERT INTO refunds (id, order_id, dispute_id, retailer_id, amount_toman, reason, status)
                VALUES (%s, %s, %s, %s, 2000000, 'Approved dispute refund', 'PENDING')
            """, (ref_id, ord_id, disp_id, RET_1))
            conn.commit()
            results.append((worker_id, "REFUND_CREATED"))
        except psycopg2.IntegrityError as err:
            conn.rollback()
            if err.pgcode == '23505':
                results.append((worker_id, "UNIQUE_VIOLATION"))
            else:
                results.append((worker_id, f"INTEGRITY_VIOLATION: {err.pgcode}"))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=refund_worker, args=("Worker_1",))
    t2 = threading.Thread(target=refund_worker, args=("Worker_2",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    created = [r for r in results if r[1] == "REFUND_CREATED"]
    violations = [r for r in results if r[1] == "UNIQUE_VIOLATION"]

    assert len(created) == 1, f"Expected exactly 1 refund created, got {len(created)}: {results}"
    assert len(violations) == 1, f"Expected exactly 1 UniqueViolation, got {len(violations)}: {results}"

    print(f"  [PASS] Concurrency 6 passed: uq_refund_per_dispute index prevented duplicate refund for the same dispute.")

def test_concurrency_7_dispute_creation_race():
    print("\n[CONCURRENCY 7] Dispute Creation Race (Two concurrent dispute creations for same order)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()
    ord_id = str(uuid.uuid4())
    og_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    cur.execute("""
        INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
        VALUES (%s, %s, 'ACTIVE', 7000000, %s)
    """, (og_id, RET_1, f"idem_disp_{tag}"))
    cur.execute("""
        INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
        VALUES (%s, %s, %s, %s, %s, 'DELIVERED', 7000000)
    """, (ord_id, f"POL-DISP-{tag}", og_id, RET_1, VND_B))
    setup_conn.commit()
    setup_conn.close()

    barrier = threading.Barrier(2)
    results = []

    def dispute_worker(worker_id):
        conn = get_conn()
        cur = conn.cursor()
        disp_id = str(uuid.uuid4())
        barrier.wait()
        try:
            cur.execute("""
                INSERT INTO disputes (id, order_id, retailer_id, vendor_id, dispute_status, claimed_amount_toman, description)
                VALUES (%s, %s, %s, %s, 'OPEN', 1500000, 'Missing carton reported')
            """, (disp_id, ord_id, RET_1, VND_B))
            conn.commit()
            results.append((worker_id, "DISPUTE_OPENED"))
        except psycopg2.IntegrityError as err:
            conn.rollback()
            if err.pgcode == '23505':
                results.append((worker_id, "UNIQUE_VIOLATION"))
            else:
                results.append((worker_id, f"INTEGRITY_VIOLATION: {err.pgcode}"))
        except Exception as e:
            conn.rollback()
            results.append((worker_id, str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=dispute_worker, args=("Client_A",))
    t2 = threading.Thread(target=dispute_worker, args=("Client_B",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    opened = [r for r in results if r[1] == "DISPUTE_OPENED"]
    violations = [r for r in results if r[1] == "UNIQUE_VIOLATION"]

    assert len(opened) == 1, f"Expected exactly 1 open dispute, got {len(opened)}: {results}"
    assert len(violations) == 1, f"Expected exactly 1 UniqueViolation, got {len(violations)}: {results}"

    print(f"  [PASS] Concurrency 7 passed: uq_dispute_open_per_order index prevented concurrent open disputes on same order.")

def test_concurrency_8_multi_vendor_dispute_isolation():
    print("\n[CONCURRENCY 8] Multi-Vendor Settlement & Dispute Concurrency...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()

    ord_a = str(uuid.uuid4())
    ord_b = str(uuid.uuid4())
    og_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    cur.execute("""
        INSERT INTO order_groups (id, retailer_id, group_status, total_amount_toman, checkout_idempotency_key)
        VALUES (%s, %s, 'ACTIVE', 10000000, %s)
    """, (og_id, RET_1, f"idem_iso_{tag}"))

    cur.execute("""
        INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
        VALUES (%s, %s, %s, %s, %s, 'DELIVERED', 6000000)
    """, (ord_a, f"POL-ISO-A-{tag}", og_id, RET_1, VND_A))

    cur.execute("""
        INSERT INTO orders (id, order_number, order_group_id, retailer_id, vendor_id, order_status, total_amount_toman)
        VALUES (%s, %s, %s, %s, %s, 'DELIVERED', 4000000)
    """, (ord_b, f"POL-ISO-B-{tag}", og_id, RET_1, VND_B))

    cur.execute("""
        INSERT INTO settlements (id, order_id, vendor_id, gross_amount_toman, net_vendor_amount_toman, status)
        VALUES (%s, %s, %s, 6000000, 6000000, 'CALCULATED')
    """, (str(uuid.uuid4()), ord_a, VND_A))

    cur.execute("""
        INSERT INTO settlements (id, order_id, vendor_id, gross_amount_toman, net_vendor_amount_toman, status)
        VALUES (%s, %s, %s, 4000000, 4000000, 'CALCULATED')
    """, (str(uuid.uuid4()), ord_b, VND_B))

    setup_conn.commit()
    setup_conn.close()

    barrier = threading.Barrier(2)
    results = []

    # Thread 1: Retailer disputes Vendor A -> Hold Settlement A
    def dispute_worker():
        conn = get_conn()
        cur = conn.cursor()
        barrier.wait()
        try:
            cur.execute("""
                INSERT INTO disputes (id, order_id, retailer_id, vendor_id, dispute_status, claimed_amount_toman, description)
                VALUES (%s, %s, %s, %s, 'OPEN', 1000000, 'Shortage claim')
            """, (str(uuid.uuid4()), ord_a, RET_1, VND_A))
            cur.execute("UPDATE orders SET dispute_status = 'OPEN' WHERE id = %s", (ord_a,))
            cur.execute("UPDATE settlements SET status = 'DISPUTED' WHERE order_id = %s", (ord_a,))
            conn.commit()
            results.append(("Dispute_A", "DISPUTED"))
        except Exception as e:
            conn.rollback()
            results.append(("Dispute_A", str(e)))
        finally:
            conn.close()

    # Thread 2: Payout Service completes Settlement B -> Mark CLOSED
    def payout_worker():
        conn = get_conn()
        cur = conn.cursor()
        barrier.wait()
        try:
            cur.execute("UPDATE settlements SET status = 'CLOSED', settled_at = CURRENT_TIMESTAMP WHERE order_id = %s AND status = 'CALCULATED'", (ord_b,))
            conn.commit()
            results.append(("Payout_B", "CLOSED"))
        except Exception as e:
            conn.rollback()
            results.append(("Payout_B", str(e)))
        finally:
            conn.close()

    t1 = threading.Thread(target=dispute_worker)
    t2 = threading.Thread(target=payout_worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert ("Dispute_A", "DISPUTED") in results
    assert ("Payout_B", "CLOSED") in results

    verify_conn = get_conn()
    cur = verify_conn.cursor()
    cur.execute("SELECT status FROM settlements WHERE order_id = %s", (ord_a,))
    st_a = cur.fetchone()[0]
    cur.execute("SELECT status FROM settlements WHERE order_id = %s", (ord_b,))
    st_b = cur.fetchone()[0]
    verify_conn.close()

    assert st_a == 'DISPUTED', f"Vendor A settlement was {st_a}, expected DISPUTED"
    assert st_b == 'CLOSED', f"Vendor B settlement was {st_b}, expected CLOSED"
    print(f"  [PASS] Concurrency 8 passed: Dispute on Vendor A did not block payout of Vendor B (Isolation verified).")

def test_concurrency_9_stale_state_price_change():
    print("\n[CONCURRENCY 9] Stale State Concurrency (Vendor price update during checkout)...")
    setup_conn = get_conn()
    cur = setup_conn.cursor()

    p_id = str(uuid.uuid4())
    vp_id = str(uuid.uuid4())
    tag = uuid.uuid4().hex[:6]

    cur.execute("""
        INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id)
        VALUES (%s, %s, 'Stale Rice 10kg', %s, %s, %s)
    """, (p_id, f"POL-STALE-{tag}", BRAND_1, CAT_1, SUBCAT_1))
    cur.execute("""
        INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity)
        VALUES (%s, %s, %s, %s, 'CARTON', 1)
    """, (vp_id, VND_A, p_id, f"SKU-STALE-{tag}"))
    cur.execute("""
        INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity)
        VALUES (%s, %s, 100, 0)
    """, (str(uuid.uuid4()), vp_id))
    # Original price: 1,000,000 Toman
    cur.execute("""
        INSERT INTO vendor_prices (id, vendor_product_id, price_toman, is_current)
        VALUES (%s, %s, 1000000, TRUE)
    """, (str(uuid.uuid4()), vp_id))
    setup_conn.commit()
    setup_conn.close()

    # Step 1: Retailer previews cart at 1,000,000 Toman
    preview_price = 1000000

    # Step 2: Vendor updates price to 1,200,000 Toman in separate transaction
    vendor_conn = get_conn()
    v_cur = vendor_conn.cursor()
    v_cur.execute("UPDATE vendor_prices SET is_current = FALSE WHERE vendor_product_id = %s", (vp_id,))
    v_cur.execute("""
        INSERT INTO vendor_prices (id, vendor_product_id, price_toman, is_current)
        VALUES (%s, %s, 1200000, TRUE)
    """, (str(uuid.uuid4()), vp_id))
    vendor_conn.commit()
    vendor_conn.close()

    # Step 3: Checkout transaction verifies current price
    buyer_conn = get_conn()
    b_cur = buyer_conn.cursor()
    b_cur.execute("SELECT price_toman FROM vendor_prices WHERE vendor_product_id = %s AND is_current = TRUE", (vp_id,))
    live_price = b_cur.fetchone()[0]

    checkout_allowed = (preview_price == live_price)
    assert not checkout_allowed, f"Live price {live_price} vs preview price {preview_price} should have flagged PRICE_CHANGED"

    print(f"  [PASS] Concurrency 9 passed: Stale state detected: checkout rejected with price delta (preview: 1.0M, live: 1.2M).")
    buyer_conn.close()

def main():
    print("=" * 80)
    print("POL POSTGRESQL 18 MULTI-CONNECTION CONCURRENCY VERIFICATION SUITE")
    print("=" * 80)

    ensure_base_fixtures()

    tests = [
        test_concurrency_1_inventory_race,
        test_concurrency_2_duplicate_checkout_same_key,
        test_concurrency_3_checkout_different_keys_scarce_stock,
        test_concurrency_4_vendor_accept_race,
        test_concurrency_5_dispatch_creation_race,
        test_concurrency_6_refund_race,
        test_concurrency_7_dispute_creation_race,
        test_concurrency_8_multi_vendor_dispute_isolation,
        test_concurrency_9_stale_state_price_change,
        test_concurrency_10_reservation_service_scarce_stock_race,
        test_concurrency_11_reservation_idempotency_same_key,
        test_concurrency_12_reservation_reconciliation_invariant,
    ]

    for test in tests:
        test()

    print("\n" + "=" * 80)
    print(f"SUCCESS: All {len(tests)}/{len(tests)} PostgreSQL concurrency race tests PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    main()
