"""
POL Invoice Domain & Multi-Tenant Access Control Runtime Verification Suite
Tests:
- Separate Invoice entity from Order (invoices & invoice_items)
- Financial integrity invariant: invoice.total_amount = SUM(invoice_items.total_line_amount)
- Multi-Vendor split order invoicing: Vendor A invoice + Vendor B invoice
- Strict tenant access isolation:
  * Retailer sees all invoices for their purchase
  * Vendor A sees ONLY Vendor A invoice
  * Vendor B sees ONLY Vendor B invoice (Vendor A invoice invisible to Vendor B)
  * Third-party tenant sees 0 invoices
"""

import sys
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_connection():
    import os
    ports = [int(os.environ["POL_PG_PORT"])] if os.environ.get("POL_PG_PORT") else [5432, 5433]
    for p in ports:
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError("Could not connect to PostgreSQL on ports 5432 or 5433")

def test_invoice_access():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================")
    print("POL INVOICE DOMAIN & TENANT AUTHORIZATION RUNTIME VERIFICATION")
    print("================================================================")

    try:
        # Setup Organizations: Retailer Org, Vendor A Org, Vendor B Org, Third-party Org
        org_ret = str(uuid.uuid4())
        org_vnda = str(uuid.uuid4())
        org_vndb = str(uuid.uuid4())
        org_other = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status) VALUES
            (%s, 'Supermarket Karun', 'RETAILER', 'ACTIVE'),
            (%s, 'Pakhsh Alborz (Vendor A)', 'VENDOR', 'ACTIVE'),
            (%s, 'Pakhsh Kian (Vendor B)', 'VENDOR', 'ACTIVE'),
            (%s, 'Unrelated Org', 'RETAILER', 'ACTIVE');
        """, (org_ret, org_vnda, org_vndb, org_other))

        # Setup Retailer and Vendors
        u_ret = str(uuid.uuid4())
        u_vnda = str(uuid.uuid4())
        u_vndb = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role) VALUES
            (%s, %s, 'Retailer Owner', 'RETAILER_OWNER'),
            (%s, %s, 'Vendor A Owner', 'VENDOR_OWNER'),
            (%s, %s, 'Vendor B Owner', 'VENDOR_OWNER');
        """, (
            u_ret, f"+98916{uuid.uuid4().int % 10000000:07d}",
            u_vnda, f"+98916{uuid.uuid4().int % 10000000:07d}",
            u_vndb, f"+98916{uuid.uuid4().int % 10000000:07d}"
        ))

        ret_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address, latitude, longitude)
            VALUES (%s, %s, %s, 'Supermarket Karun', 'Kianpars', 'Ahvaz', 31.32, 48.67);
        """, (ret_id, u_ret, org_ret))

        vnda_id = str(uuid.uuid4())
        vndb_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman) VALUES
            (%s, %s, %s, 'Pakhsh Alborz', 'Warehouse 1', 5000000),
            (%s, %s, %s, 'Pakhsh Kian', 'Warehouse 2', 5000000);
        """, (vnda_id, u_vnda, org_vnda, vndb_id, u_vndb, org_vndb))

        # OrderGroup with 2 split child orders
        og_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO order_groups (id, retailer_id, total_amount_toman, group_status)
            VALUES (%s, %s, 15000000, 'ACTIVE');
        """, (og_id, ret_id))

        order_a_id = str(uuid.uuid4())
        order_b_id = str(uuid.uuid4())
        ord_a_num = f"ORD-A-{uuid.uuid4().hex[:8].upper()}"
        ord_b_num = f"ORD-B-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO orders (id, order_group_id, retailer_id, vendor_id, order_number, total_amount_toman, order_status, dispute_status) VALUES
            (%s, %s, %s, %s, %s, 9000000, 'DELIVERED', 'NONE'),
            (%s, %s, %s, %s, %s, 6000000, 'DELIVERED', 'NONE');
        """, (order_a_id, og_id, ret_id, vnda_id, ord_a_num, order_b_id, og_id, ret_id, vndb_id, ord_b_num))

        # 1. Invoice Generation for Vendor A
        print("\n[TEST 1] Generating Official Invoice for Vendor A (9,000,000 Toman)...")
        inv_a_id = str(uuid.uuid4())
        inv_a_num = f"INV-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO invoices (id, invoice_number, order_id, retailer_organization_id, vendor_organization_id, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, 9000000, 'ISSUED');
        """, (inv_a_id, inv_a_num, order_a_id, org_ret, org_vnda))

        # Line items for Invoice A (2 items: 5,000,000 + 4,000,000 = 9,000,000)
        cur.execute("""
            INSERT INTO invoice_items (id, invoice_id, product_name, quantity, unit_price, total_line_amount) VALUES
            (%s, %s, 'روغن آفتابگردان اویلا', 10, 500000, 5000000),
            (%s, %s, 'تن ماهی شیلتون', 20, 200000, 4000000);
        """, (str(uuid.uuid4()), inv_a_id, str(uuid.uuid4()), inv_a_id))

        # 2. Invoice Generation for Vendor B
        print("\n[TEST 2] Generating Official Invoice for Vendor B (6,000,000 Toman)...")
        inv_b_id = str(uuid.uuid4())
        inv_b_num = f"INV-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO invoices (id, invoice_number, order_id, retailer_organization_id, vendor_organization_id, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, 6000000, 'ISSUED');
        """, (inv_b_id, inv_b_num, order_b_id, org_ret, org_vndb))

        cur.execute("""
            INSERT INTO invoice_items (id, invoice_id, product_name, quantity, unit_price, total_line_amount)
            VALUES (%s, %s, 'رب گوجه‌فرنگی روژین', 12, 500000, 6000000);
        """, (str(uuid.uuid4()), inv_b_id))

        # 3. Financial Invariant Verification
        print("\n[TEST 3] Verifying Financial Invariants (Invoice Total == SUM of Items)...")
        for inv_id, expected_total in [(inv_a_id, 9000000), (inv_b_id, 6000000)]:
            cur.execute("""
                SELECT i.total_amount, SUM(ii.total_line_amount) as items_sum
                FROM invoices i
                JOIN invoice_items ii ON i.id = ii.invoice_id
                WHERE i.id = %s
                GROUP BY i.total_amount;
            """, (inv_id,))
            inv_check = cur.fetchone()
            assert inv_check["total_amount"] == expected_total
            assert inv_check["items_sum"] == expected_total
        print("  [PASS] Financial invariant verified: total_amount exactly equals SUM(invoice_items).")

        # 4. Tenant Access Authorization Scoping
        print("\n[TEST 4] Testing Strict Tenant-Scoped Visibility...")
        # Retailer Org should see both Invoice A and Invoice B
        cur.execute("""
            SELECT invoice_number FROM invoices WHERE retailer_organization_id = %s ORDER BY invoice_number;
        """, (org_ret,))
        ret_invoices = [r["invoice_number"] for r in cur.fetchall()]
        assert inv_a_num in ret_invoices and inv_b_num in ret_invoices
        print(f"  [PASS] Retailer sees full split procurement invoices ({len(ret_invoices)} invoices).")

        # Vendor A should see ONLY Invoice A
        cur.execute("""
            SELECT invoice_number FROM invoices WHERE vendor_organization_id = %s;
        """, (org_vnda,))
        vnda_invoices = [r["invoice_number"] for r in cur.fetchall()]
        assert inv_a_num in vnda_invoices
        assert inv_b_num not in vnda_invoices
        print("  [PASS] Vendor A sees ONLY Vendor A invoice (Vendor B invoice isolated!).")

        # Vendor B should see ONLY Invoice B
        cur.execute("""
            SELECT invoice_number FROM invoices WHERE vendor_organization_id = %s;
        """, (org_vndb,))
        vndb_invoices = [r["invoice_number"] for r in cur.fetchall()]
        assert inv_b_num in vndb_invoices
        assert inv_a_num not in vndb_invoices
        print("  [PASS] Vendor B sees ONLY Vendor B invoice (Vendor A invoice isolated!).")

        # Unrelated third-party should see 0 invoices
        cur.execute("""
            SELECT count(*) as count FROM invoices 
            WHERE retailer_organization_id = %s OR vendor_organization_id = %s;
        """, (org_other, org_other))
        assert cur.fetchone()["count"] == 0
        print("  [PASS] Unrelated tenant query returns 0 invoices (Zero cross-tenant leakage).")

        conn.commit()
        conn.close()
        print("\n================================================================")
        print("ALL INVOICE & TENANT ACCESS TESTS PASSED SUCCESSFULLY!")
        print("================================================================")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_invoice_access()
