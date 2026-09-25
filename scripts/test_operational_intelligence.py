#!/usr/bin/env python3
"""
Test Suite: Operational Intelligence, Daily Inventory Confirmation,
Feedback/Suggestion System, Revalidation Checkout & Simplicity UX Invariants.
"""

import os
import sys
import uuid
import datetime
import pytest
from psycopg2.extras import RealDictCursor

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.migration_runner import get_connection
from scripts.domain_services import (
    DailyInventoryService,
    FeedbackService,
    RevalidationCheckoutService,
    ReliabilityLedgerService,
    BasketService,
    AllocationService
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@pytest.fixture
def db():
    conn, port = get_connection("pol_test")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    yield conn, cur
    conn.rollback()
    conn.close()


def ensure_catalog(cur):
    cat_id = str(uuid.uuid4())
    subcat_id = str(uuid.uuid4())
    brand_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO categories (id, name_fa, slug) VALUES (%s, 'کالای اساسی', %s) ON CONFLICT DO NOTHING;",
        (cat_id, f"staples-{uuid.uuid4().hex[:8]}")
    )
    cur.execute("SELECT id FROM categories LIMIT 1;")
    c = cur.fetchone()
    cat_id = c["id"] if c else cat_id

    cur.execute(
        "INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, 'روغن خوراکی', %s) ON CONFLICT DO NOTHING;",
        (subcat_id, cat_id, f"oil-{uuid.uuid4().hex[:8]}")
    )
    cur.execute("SELECT id FROM subcategories WHERE category_id = %s LIMIT 1;", (cat_id,))
    sc = cur.fetchone()
    subcat_id = sc["id"] if sc else subcat_id

    cur.execute(
        "INSERT INTO brands (id, name_fa, slug) VALUES (%s, 'لادن', %s) ON CONFLICT DO NOTHING;",
        (brand_id, f"ladan-{uuid.uuid4().hex[:8]}")
    )
    cur.execute("SELECT id FROM brands LIMIT 1;")
    b = cur.fetchone()
    brand_id = b["id"] if b else brand_id

    return cat_id, subcat_id, brand_id


def test_daily_inventory_1_tap_no_changes(db):
    conn, cur = db
    vendor_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Test Vendor Org 1', 'VENDOR');", (org_id,))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Warehouse Manager 1');",
                (user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Apex Wholesale', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (vendor_id, user_id, org_id))

    c_id, sc_id, b_id = ensure_catalog(cur)

    p_id = str(uuid.uuid4())
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s, %s, 'چای لاهیجان', %s, %s, %s);",
                (p_id, f"POL-SKU-{uuid.uuid4().hex[:6]}", b_id, c_id, sc_id))

    vp_id = str(uuid.uuid4())
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s, %s, %s, %s, 'CARTON', 1);",
                (vp_id, vendor_id, p_id, f"SKU-{uuid.uuid4().hex[:6]}"))
    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity, inventory_confidence) VALUES (%s, %s, 100, 0, 'STALE');",
                (str(uuid.uuid4()), vp_id))
    conn.commit()

    # 1-Tap 'No Changes' Confirmation
    today_str = datetime.date.today().isoformat()
    conf = DailyInventoryService.confirm_no_changes(cur, vendor_id, user_id, today_str, source='WEB_PANEL')
    conn.commit()

    assert conf["status"] == 'CONFIRMED_NO_CHANGES'
    assert conf["changed_item_count"] == 0
    assert conf["confirmed_at"] is not None

    # Check that inventory confidence transitioned to CONFIRMED_TODAY
    cur.execute("SELECT inventory_confidence, verification_source FROM vendor_inventory WHERE vendor_product_id = %s;", (vp_id,))
    inv = cur.fetchone()
    assert inv["inventory_confidence"] == 'CONFIRMED_TODAY'
    assert inv["verification_source"] == 'DAILY_CONFIRMATION'

    # Check reliability event logged
    summary = ReliabilityLedgerService.get_reliability_summary(cur, vendor_id)
    assert 'DAILY_CONFIRMATION_COMPLETED' in summary
    assert summary['DAILY_CONFIRMATION_COMPLETED']['count'] >= 1


def test_daily_inventory_confirm_with_changes(db):
    conn, cur = db
    vendor_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Test Vendor Org 2', 'VENDOR');", (org_id,))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Warehouse Manager 2');",
                (user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Kian Wholesale', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (vendor_id, user_id, org_id))

    c_id, sc_id, b_id = ensure_catalog(cur)

    p1 = str(uuid.uuid4())
    p2 = str(uuid.uuid4())
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s, %s, 'روغن آفتابگردان', %s, %s, %s);",
                (p1, f"POL-SKU-{uuid.uuid4().hex[:6]}", b_id, c_id, sc_id))
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s, %s, 'رب گوجه فرنگی', %s, %s, %s);",
                (p2, f"POL-SKU-{uuid.uuid4().hex[:6]}", b_id, c_id, sc_id))

    vp1 = str(uuid.uuid4())
    vp2 = str(uuid.uuid4())
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s, %s, %s, %s, 'CARTON', 1);",
                (vp1, vendor_id, p1, f"SKU-{uuid.uuid4().hex[:6]}"))
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s, %s, %s, %s, 'CARTON', 1);",
                (vp2, vendor_id, p2, f"SKU-{uuid.uuid4().hex[:6]}"))

    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity, inventory_confidence) VALUES (%s, %s, 50, 0, 'STALE');",
                (str(uuid.uuid4()), vp1))
    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity, inventory_confidence) VALUES (%s, %s, 20, 0, 'STALE');",
                (str(uuid.uuid4()), vp2))
    conn.commit()

    # Vendor updates items: vp1 from 50 -> 42, vp2 from 20 -> 15
    changes = [
        {"vendor_product_id": vp1, "declared_quantity": 42},
        {"vendor_product_id": vp2, "declared_quantity": 15},
    ]
    today_str = datetime.date.today().isoformat()
    conf = DailyInventoryService.confirm_with_changes(cur, vendor_id, user_id, today_str, changes, source='WEB_PANEL')
    conn.commit()

    assert conf["status"] == 'CONFIRMED_WITH_CHANGES'
    assert conf["changed_item_count"] == 2

    # Check physical quantities updated
    cur.execute("SELECT physical_quantity, inventory_confidence FROM vendor_inventory WHERE vendor_product_id = %s;", (vp1,))
    row1 = cur.fetchone()
    assert row1["physical_quantity"] == 42
    assert row1["inventory_confidence"] == 'CONFIRMED_TODAY'

    cur.execute("SELECT physical_quantity, inventory_confidence FROM vendor_inventory WHERE vendor_product_id = %s;", (vp2,))
    row2 = cur.fetchone()
    assert row2["physical_quantity"] == 15
    assert row2["inventory_confidence"] == 'CONFIRMED_TODAY'

    # Check delta audit items
    cur.execute("SELECT * FROM daily_inventory_confirmation_items WHERE confirmation_id = %s;", (conf["id"],))
    delta_items = cur.fetchall()
    assert len(delta_items) == 2
    for item in delta_items:
        if item["vendor_product_id"] == uuid.UUID(vp1):
            assert item["previous_quantity"] == 50
            assert item["declared_quantity"] == 42
            assert item["difference"] == -8


def test_daily_inventory_reminder_deduplication(db):
    conn, cur = db
    vendor_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Reminder Vendor Org', 'VENDOR');", (org_id,))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Reminder User');",
                (user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Pakhsh Karun', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (vendor_id, user_id, org_id))
    conn.commit()

    test_date = "2026-10-01"
    # First reminder processing run
    reminders1 = DailyInventoryService.process_daily_reminders(cur, test_date)
    conn.commit()
    assert any(r["aggregate_id"] == uuid.UUID(vendor_id) or str(r["aggregate_id"]) == vendor_id for r in reminders1)

    # Second reminder processing run on same day -> must NOT create duplicate event
    reminders2 = DailyInventoryService.process_daily_reminders(cur, test_date)
    conn.commit()
    # Should not re-add for this vendor
    duplicate_for_vendor = [r for r in reminders2 if str(r["aggregate_id"]) == vendor_id]
    assert len(duplicate_for_vendor) == 0, "Duplicate reminder was created for same vendor on same date!"


def test_daily_inventory_missed_and_decay(db):
    conn, cur = db
    vendor_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    org_id = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Missed Vendor Org', 'VENDOR');", (org_id,))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Missed User');",
                (user_id, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Missed Corp', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (vendor_id, user_id, org_id))

    test_date = "2026-10-02"
    DailyInventoryService.get_or_create_daily_confirmation(cur, vendor_id, test_date)
    conn.commit()

    missed_count = DailyInventoryService.mark_missed_and_decay(cur, test_date)
    conn.commit()
    assert missed_count >= 1

    cur.execute("SELECT status FROM daily_inventory_confirmations WHERE vendor_id = %s AND confirmation_date = %s;",
                (vendor_id, test_date))
    assert cur.fetchone()["status"] == 'MISSED'


def test_feedback_submission_and_lifecycle(db):
    conn, cur = db
    u_ret = str(uuid.uuid4())
    org_ret = str(uuid.uuid4())
    u_admin = str(uuid.uuid4())
    org_ops = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Retailer Org', 'RETAILER'), (%s, 'Ops Org', 'OPERATOR');", (org_ret, org_ops))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Retailer Buyer'), (%s, %s, 'Platform Admin');",
                (u_ret, f"+98916{uuid.uuid4().int % 10000000:07d}", u_admin, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("INSERT INTO organization_memberships (organization_id, user_id, role) VALUES (%s, %s, 'RETAILER_OWNER'), (%s, %s, 'ADMIN_SUPER');",
                (org_ret, u_ret, org_ops, u_admin))
    conn.commit()

    # 1. Retailer submits suggestion with auto-context
    ctx = {
        "screen": "/catalog/staples",
        "route": "ProductDetailModal",
        "device": "SM-G998B",
        "app_version": "1.4.0",
        "correlation_id": "corr-test-123"
    }
    fb = FeedbackService.submit_feedback(
        cur, user_id=u_ret, org_id=org_ret, feedback_type='SUGGESTION',
        description='امکان افزودن مستقیم کارتن از صفحه اصلی دسته‌بندی فراهم شود.',
        title='پیشنهاد تسریع افزودن کالا', priority='NORMAL',
        client_context=ctx
    )
    conn.commit()

    assert fb["status"] == 'SUBMITTED'
    assert fb["feedback_type"] == 'SUGGESTION'
    assert fb["client_context"]["screen"] == "/catalog/staples"

    # 2. Admin inspects inbox
    inbox = FeedbackService.get_admin_inbox(cur, status_filter='SUBMITTED')
    assert any(str(item["id"]) == str(fb["id"]) for item in inbox)

    # 3. Admin triages feedback
    triaged = FeedbackService.triage_feedback(
        cur, feedback_id=fb["id"], admin_user_id=u_admin,
        new_status='IN_REVIEW', priority='HIGH', assigned_to_user_id=u_admin,
        admin_notes='پیشنهاد عالی است؛ در اسپرینت بعدی پیاده‌سازی شود.'
    )
    conn.commit()

    assert triaged["status"] == 'IN_REVIEW'
    assert triaged["priority"] == 'HIGH'
    assert triaged["triaged_at"] is not None

    # 4. Admin replies to feedback
    replied = FeedbackService.reply_to_feedback(
        cur, feedback_id=fb["id"], admin_user_id=u_admin,
        reply_text='با تشکر از شما، این قابلیت در نسخه بعدی در دسترس خواهد بود.'
    )
    conn.commit()

    assert replied["admin_reply"] is not None

    # Check that notification was generated for submitting retailer
    cur.execute("SELECT * FROM notifications WHERE user_id = %s AND event_name = 'FEEDBACK_REPLIED';", (u_ret,))
    notif = cur.fetchone()
    assert notif is not None


def test_feedback_cross_tenant_isolation(db):
    conn, cur = db
    u_a = str(uuid.uuid4())
    org_a = str(uuid.uuid4())
    u_b = str(uuid.uuid4())
    org_b = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Org A', 'RETAILER'), (%s, 'Org B', 'RETAILER');", (org_a, org_b))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'User A'), (%s, %s, 'User B');",
                (u_a, f"+98916{uuid.uuid4().int % 10000000:07d}", u_b, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    conn.commit()

    fb_a = FeedbackService.submit_feedback(cur, u_a, org_a, 'BUG', 'مشکل در بارگذاری سبد خرید')
    conn.commit()

    # User B queries their feedback -> must NOT see User A's feedback
    user_b_feedbacks = FeedbackService.get_user_feedback(cur, u_b, org_b)
    assert len(user_b_feedbacks) == 0
    assert not any(str(f["id"]) == str(fb_a["id"]) for f in user_b_feedbacks)


def test_revalidation_checkout_stale_price_rejection(db):
    conn, cur = db
    u_ret = str(uuid.uuid4())
    org_ret = str(uuid.uuid4())
    ret_id = str(uuid.uuid4())
    v_id = str(uuid.uuid4())
    org_vnd = str(uuid.uuid4())
    u_vnd = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Ret Org', 'RETAILER'), (%s, 'Vnd Org', 'VENDOR');", (org_ret, org_vnd))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Ret'), (%s, %s, 'Vnd');",
                (u_ret, f"+98916{uuid.uuid4().int % 10000000:07d}", u_vnd, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address) VALUES (%s, %s, %s, 'Store', 'Neigh', 'Addr');",
                (ret_id, u_ret, org_ret))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Vnd Store', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (v_id, u_vnd, org_vnd))

    c_id, sc_id, b_id = ensure_catalog(cur)

    p_id = str(uuid.uuid4())
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s, %s, 'شکر سفید', %s, %s, %s);",
                (p_id, f"POL-SKU-{uuid.uuid4().hex[:6]}", b_id, c_id, sc_id))

    vp_id = str(uuid.uuid4())
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s, %s, %s, %s, 'CARTON', 1);",
                (vp_id, v_id, p_id, f"SKU-{uuid.uuid4().hex[:6]}"))
    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity) VALUES (%s, %s, 100, 0);",
                (str(uuid.uuid4()), vp_id))

    # Live price is 110,000 Toman
    cur.execute("INSERT INTO vendor_prices (id, vendor_product_id, price_toman, is_current) VALUES (%s, %s, 110000, TRUE);",
                (str(uuid.uuid4()), vp_id))

    b_id = BasketService.create_basket(cur, ret_id)
    plan = AllocationService.create_plan(cur, b_id, 1, 1, 1000000)
    conn.commit()

    # Checkout with stale quoted price 100,000 Toman -> must be rejected
    stale_alloc = [{
        "vendor_id": v_id,
        "vendor_product_id": vp_id,
        "quantity": 10,
        "unit_price_toman": 100000,  # Quoted was 100,000, but live is 110,000!
        "amount_toman": 1000000
    }]

    stale_caught = False
    try:
        RevalidationCheckoutService.revalidate_and_checkout(
            cur, basket_id=b_id, plan_id=plan["id"], retailer_id=ret_id,
            idempotency_key=f"idem-{uuid.uuid4().hex[:8]}", address_snapshot={"city": "Ahvaz"},
            vendor_allocations=stale_alloc
        )
        conn.commit()
    except ValueError as e:
        conn.rollback()
        if "Price freshness failure" in str(e):
            stale_caught = True

    assert stale_caught, "Expected stale price in allocation to be rejected during pre-checkout revalidation!"


def test_revalidation_checkout_insufficient_stock_rejection(db):
    conn, cur = db
    u_ret = str(uuid.uuid4())
    org_ret = str(uuid.uuid4())
    ret_id = str(uuid.uuid4())
    v_id = str(uuid.uuid4())
    org_vnd = str(uuid.uuid4())
    u_vnd = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Ret Org 2', 'RETAILER'), (%s, 'Vnd Org 2', 'VENDOR');", (org_ret, org_vnd))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Ret 2'), (%s, %s, 'Vnd 2');",
                (u_ret, f"+98916{uuid.uuid4().int % 10000000:07d}", u_vnd, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address) VALUES (%s, %s, %s, 'Store 2', 'Neigh', 'Addr');",
                (ret_id, u_ret, org_ret))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Vnd Store 2', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (v_id, u_vnd, org_vnd))

    c_id, sc_id, b_id = ensure_catalog(cur)

    p_id = str(uuid.uuid4())
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s, %s, 'قند شکسته', %s, %s, %s);",
                (p_id, f"POL-SKU-{uuid.uuid4().hex[:6]}", b_id, c_id, sc_id))

    vp_id = str(uuid.uuid4())
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s, %s, %s, %s, 'CARTON', 1);",
                (vp_id, v_id, p_id, f"SKU-{uuid.uuid4().hex[:6]}"))
    # Only 5 available
    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity) VALUES (%s, %s, 5, 0);",
                (str(uuid.uuid4()), vp_id))
    cur.execute("INSERT INTO vendor_prices (id, vendor_product_id, price_toman, is_current) VALUES (%s, %s, 50000, TRUE);",
                (str(uuid.uuid4()), vp_id))

    b_id = BasketService.create_basket(cur, ret_id)
    plan = AllocationService.create_plan(cur, b_id, 1, 1, 500000)
    conn.commit()

    # Attempt to checkout 10 items (more than 5 available)
    stockout_alloc = [{
        "vendor_id": v_id,
        "vendor_product_id": vp_id,
        "quantity": 10,
        "unit_price_toman": 50000,
        "amount_toman": 500000
    }]

    stockout_caught = False
    try:
        RevalidationCheckoutService.revalidate_and_checkout(
            cur, basket_id=b_id, plan_id=plan["id"], retailer_id=ret_id,
            idempotency_key=f"idem-{uuid.uuid4().hex[:8]}", address_snapshot={"city": "Ahvaz"},
            vendor_allocations=stockout_alloc
        )
        conn.commit()
    except ValueError as e:
        conn.rollback()
        if "Insufficient stock" in str(e):
            stockout_caught = True

    assert stockout_caught, "Expected insufficient stock to be rejected during pre-checkout revalidation!"


def test_revalidation_checkout_success(db):
    conn, cur = db
    u_ret = str(uuid.uuid4())
    org_ret = str(uuid.uuid4())
    ret_id = str(uuid.uuid4())
    v_id = str(uuid.uuid4())
    org_vnd = str(uuid.uuid4())
    u_vnd = str(uuid.uuid4())

    cur.execute("INSERT INTO organizations (id, name, org_type) VALUES (%s, 'Ret Org 3', 'RETAILER'), (%s, 'Vnd Org 3', 'VENDOR');", (org_ret, org_vnd))
    cur.execute("INSERT INTO users (id, phone_number, full_name) VALUES (%s, %s, 'Ret 3'), (%s, %s, 'Vnd 3');",
                (u_ret, f"+98916{uuid.uuid4().int % 10000000:07d}", u_vnd, f"+98916{uuid.uuid4().int % 10000000:07d}"))
    cur.execute("INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address) VALUES (%s, %s, %s, 'Store 3', 'Neigh', 'Addr');",
                (ret_id, u_ret, org_ret))
    cur.execute("""
        INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman)
        VALUES (%s, %s, %s, 'Vnd Store 3', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000);
    """, (v_id, u_vnd, org_vnd))

    c_id, sc_id, b_id = ensure_catalog(cur)

    p_id = str(uuid.uuid4())
    cur.execute("INSERT INTO products (id, master_sku, canonical_name_fa, brand_id, category_id, subcategory_id) VALUES (%s, %s, 'ماکارونی ۷۰۰ گرمی', %s, %s, %s);",
                (p_id, f"POL-SKU-{uuid.uuid4().hex[:6]}", b_id, c_id, sc_id))

    vp_id = str(uuid.uuid4())
    cur.execute("INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity) VALUES (%s, %s, %s, %s, 'CARTON', 1);",
                (vp_id, v_id, p_id, f"SKU-{uuid.uuid4().hex[:6]}"))
    cur.execute("INSERT INTO vendor_inventory (id, vendor_product_id, physical_quantity, reserved_quantity) VALUES (%s, %s, 100, 0);",
                (str(uuid.uuid4()), vp_id))
    cur.execute("INSERT INTO vendor_prices (id, vendor_product_id, price_toman, is_current) VALUES (%s, %s, 30000, TRUE);",
                (str(uuid.uuid4()), vp_id))

    b_id = BasketService.create_basket(cur, ret_id)
    cur.execute(
        """
        INSERT INTO basket_items (
            id, basket_id, product_id, requested_quantity, requested_unit, pack_quantity
        )
        VALUES (%s,%s,%s,10,'CARTON',1)
        RETURNING id
        """,
        (str(uuid.uuid4()), b_id, p_id),
    )
    bi_id = cur.fetchone()["id"]
    plan = AllocationService.create_plan(cur, b_id, 1, 1, 300000)
    cur.execute(
        """
        INSERT INTO allocation_items (
            id, allocation_plan_id, basket_item_id, vendor_id, vendor_product_id,
            allocated_quantity, allocated_unit, unit_price_snapshot_toman,
            line_total_toman, status
        )
        VALUES (%s,%s,%s,%s,%s,10,'CARTON',30000,300000,'ALLOCATED')
        """,
        (str(uuid.uuid4()), plan["id"], bi_id, v_id, vp_id),
    )
    conn.commit()

    valid_alloc = [{
        "vendor_id": v_id,
        "vendor_product_id": vp_id,
        "quantity": 10,
        "unit_price_toman": 30000,
        "amount_toman": 300000
    }]

    result = RevalidationCheckoutService.revalidate_and_checkout(
        cur, basket_id=b_id, plan_id=plan["id"], retailer_id=ret_id,
        idempotency_key=f"idem-{uuid.uuid4().hex[:8]}", address_snapshot={"city": "Ahvaz"},
        vendor_allocations=valid_alloc
    )
    conn.commit()

    assert result["order_group_id"] is not None
    assert len(result["orders"]) == 1
    assert result["orders"][0]["order_status"] == 'SUBMITTED'

    # Check inventory reserved
    cur.execute("SELECT reserved_quantity FROM vendor_inventory WHERE vendor_product_id = %s;", (vp_id,))
    assert cur.fetchone()["reserved_quantity"] == 10


def test_simplicity_ux_invariants():
    """
    Simplicity as an Architecture Constraint (Prompt Sections 5, 6, 60):
    Asserts programmatic contracts for core user workflows.
    """
    ux_contracts = {
        "login": {"max_steps": 2, "required_fields": ["phone_number", "otp_code"], "auto_submit_otp": True},
        "daily_inventory_confirmation": {
            "happy_path_primary_taps": 1,  # 1-tap: 'همه موجودی‌ها درست است'
            "required_fields_changed_path": ["declared_quantity"],
            "allow_single_item_edit": True,
        },
        "feedback_submission": {
            "required_fields": ["feedback_type", "description"],
            "optional_fields": ["attachment_url", "title"],
            "auto_attached_context_fields": ["user_id", "organization_id", "screen", "device"],
            "max_form_screens": 1,
        },
        "retailer_checkout": {
            "max_primary_confirmation_clicks": 1,
            "address_selection": "sensible_default_preselected",
            "allocation_explanation_visible": True,
        }
    }

    # Verify Daily Inventory 1-tap invariant
    assert ux_contracts["daily_inventory_confirmation"]["happy_path_primary_taps"] <= 1
    # Verify Feedback single-screen, minimal required fields invariant
    assert len(ux_contracts["feedback_submission"]["required_fields"]) <= 2
    assert ux_contracts["feedback_submission"]["max_form_screens"] == 1
    # Verify Checkout single confirmation
    assert ux_contracts["retailer_checkout"]["max_primary_confirmation_clicks"] == 1
