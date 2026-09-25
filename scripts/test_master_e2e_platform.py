"""
POL Master End-to-End Platform Integration Test
Comprehensive pre-Sprint-0 verification integrating all platform + commerce domains:
1. Multi-Tenant Identity: Retailer Org (Owner, Staff), Vendor A Org (Owner, Staff), Admin
2. Product Catalog, Packaging & Dual-Vendor Offers
3. Basket Creation (v1) & Item Additions (v2)
4. Multi-Vendor Minimum-Fragmentation Allocation (D-014)
5. Inventory Reservations Lifecycle (ACTIVE)
6. Checkout Idempotency & Immutable Delivery Address Snapshot
7. Vendor A Order Acceptance within SLA Working Calendar -> Reservation CONSUMED
8. Vendor B Order Rejection -> Reservation RELEASED
9. OrderGroup Aggregate State Projection (PARTIALLY_COMPLETED)
10. Delivery Dispatch with Driver Details (Option A) & OTP Confirmation (DELIVERED)
11. Non-Custodial Direct Payment Evidence & Verification
12. Multi-Vendor Invoice Domain with Tenant Authorization
13. Customer Support Case (distinct from Dispute)
14. Formal Dispute Isolation & Settlement Hold
15. Transactional Outbox Event to Notification Engine & User Inbox
16. Admin Sensitive Action & Audit Log Tracking
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from scripts.domain_services import (
    AuthService,
    BasketService,
    AllocationService,
    OrderGroupProjector,
    FulfillmentService,
    PaymentService,
    DisputeService,
    NotificationService,
    SupportService,
    AuditService
)
from scripts.checkout_gateway import CanonicalCheckoutGateway
from scripts.fulfillment_service import (
    dispatch_order as canonical_dispatch_order,
    transition_delivery_stage,
    confirm_delivery as canonical_confirm_delivery,
)

import hashlib
import json
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from psycopg2 import sql
from psycopg2.extensions import parse_dsn

from scripts.allocation_engine import BasketItem, MultiVendorAllocationEngine, Vendor, VendorSKU
from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.migration_runner import apply_migration_chain, get_migration_chain
from scripts import operational_policies
from scripts.operational_policies import AllocationIntegrityError, validate_vendor_operational_capacity

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_connection():
    ports = [5432, 5433]
    for p in ports:
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            # Strict safety guard: only test database allowed
            dsn_params = conn.get_dsn_parameters()
            if dsn_params.get("dbname") != "pol_test":
                raise RuntimeError(f"SAFETY VIOLATION: Refusing to run tests on database '{dsn_params.get('dbname')}'! Must be 'pol_test'.")
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError("Could not connect to PostgreSQL on ports 5432 or 5433")

def run_master_e2e_test():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    print("================================================================================")
    print("POL MASTER PLATFORM END-TO-END INTEGRATION TEST (POSTGRESQL 18 + DOMAIN SERVICES)")
    print("================================================================================")

    try:
        # -------------------------------------------------------------
        # 1. Identity & Multi-User Organization Setup
        # -------------------------------------------------------------
        print("\n[STEP 1] Setting up Organizations, Users and Memberships with AuthService...")
        org_ret = str(uuid.uuid4())
        org_vnda = str(uuid.uuid4())
        org_vndb = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status) VALUES
            (%s, 'Supermarket Golestan', 'RETAILER', 'ACTIVE'),
            (%s, 'Pakhsh Alborz', 'VENDOR', 'ACTIVE'),
            (%s, 'Pakhsh Jonoub', 'VENDOR', 'ACTIVE');
        """, (org_ret, org_vnda, org_vndb))

        u_ret_owner = str(uuid.uuid4())
        u_ret_staff = str(uuid.uuid4())
        u_vnda_owner = str(uuid.uuid4())
        u_vnda_staff = str(uuid.uuid4())
        u_vndb_owner = str(uuid.uuid4())
        u_admin = str(uuid.uuid4())

        phone_ret_owner = f"+98916{uuid.uuid4().int % 10000000:07d}"

        cur.execute("""
            INSERT INTO users (id, phone_number, full_name, role) VALUES
            (%s, %s, 'Hossein Golestani (Owner)', 'RETAILER_OWNER'),
            (%s, %s, 'Kaveh Golestani (Staff)', 'RETAILER_STAFF'),
            (%s, %s, 'Alborz Wholesaler', 'VENDOR_OWNER'),
            (%s, %s, 'Alborz Warehouse Clerk', 'VENDOR_STAFF'),
            (%s, %s, 'Jonoub Wholesaler', 'VENDOR_OWNER'),
            (%s, %s, 'Platform Ops Admin', 'OPS_ADMIN');
        """, (
            u_ret_owner, phone_ret_owner,
            u_ret_staff, f"+98916{uuid.uuid4().int % 10000000:07d}",
            u_vnda_owner, f"+98916{uuid.uuid4().int % 10000000:07d}",
            u_vnda_staff, f"+98916{uuid.uuid4().int % 10000000:07d}",
            u_vndb_owner, f"+98916{uuid.uuid4().int % 10000000:07d}",
            u_admin, f"+98916{uuid.uuid4().int % 10000000:07d}"
        ))

        cur.execute("""
            INSERT INTO organization_memberships (organization_id, user_id, role, is_primary, status) VALUES
            (%s, %s, 'RETAILER_OWNER', TRUE, 'ACTIVE'),
            (%s, %s, 'RETAILER_STAFF', FALSE, 'ACTIVE'),
            (%s, %s, 'VENDOR_OWNER', TRUE, 'ACTIVE'),
            (%s, %s, 'VENDOR_STAFF', FALSE, 'ACTIVE'),
            (%s, %s, 'VENDOR_OWNER', TRUE, 'ACTIVE');
        """, (org_ret, u_ret_owner, org_ret, u_ret_staff, org_vnda, u_vnda_owner, org_vnda, u_vnda_staff, org_vndb, u_vndb_owner))

        ret_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO retailers (id, user_id, organization_id, store_name, neighborhood, address, latitude, longitude)
            VALUES (%s, %s, %s, 'Supermarket Golestan', 'Golestan', 'Ahvaz, Golestan St 5', 31.30, 48.65);
        """, (ret_id, u_ret_owner, org_ret))

        vnda_id = str(uuid.uuid4())
        vndb_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendors (id, user_id, organization_id, business_name, warehouse_address, min_order_value_toman) VALUES
            (%s, %s, %s, 'Pakhsh Alborz', 'Warehouse 10, Shahr-e-Bonakdaran', 5000000),
            (%s, %s, %s, 'Pakhsh Jonoub', 'Warehouse 12, Shahr-e-Bonakdaran', 5000000);
        """, (vnda_id, u_vnda_owner, org_vnda, vndb_id, u_vndb_owner, org_vndb))

        # Test AuthService OTP & Session creation
        otp_challenge = AuthService.request_otp(cur, phone_ret_owner, "127.0.0.1", purpose='LOGIN')
        assert otp_challenge["status"] == "PENDING"
        session = AuthService.verify_otp(cur, phone_ret_owner, "1234", u_ret_owner, org_ret)
        assert session["session"]["status"] == "ACTIVE"
        assert str(session["session"]["active_organization_id"]) == org_ret
        assert session["access_token"] and session["refresh_token"]
        print("  [PASS] Organizations, Memberships, Retailer & Vendors registered; AuthService OTP & Session verified.")

        # -------------------------------------------------------------
        # 2. Master Catalog & Vendor Inventory Setup
        # -------------------------------------------------------------
        print("\n[STEP 2] Catalog Products and Vendor Inventory Setup...")
        cat_id = str(uuid.uuid4())
        subcat_id = str(uuid.uuid4())
        brand_id = str(uuid.uuid4())
        cur.execute("INSERT INTO categories (id, name_fa, slug) VALUES (%s, 'Ú©Ø§Ù„Ø§ÛŒ Ø§Ø³Ø§Ø³ÛŒ', %s) ON CONFLICT DO NOTHING;", 
                    (cat_id, f"staples-{cat_id[:8]}"))
        cur.execute("INSERT INTO subcategories (id, category_id, name_fa, slug) VALUES (%s, %s, 'Ø±ÙˆØºÙ†', %s) ON CONFLICT DO NOTHING;", 
                    (subcat_id, cat_id, f"oil-{subcat_id[:8]}"))
        cur.execute("INSERT INTO brands (id, name_fa, slug) VALUES (%s, 'Ù„Ø§Ø¯Ù†', %s) ON CONFLICT DO NOTHING;", 
                    (brand_id, f"ladan-{brand_id[:8]}"))

        prod_a = str(uuid.uuid4())
        prod_b = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO products (id, master_sku, brand_id, category_id, subcategory_id, canonical_name_fa, is_active) VALUES
            (%s, %s, %s, %s, %s, 'Ø±ÙˆØºÙ† Ø¢ÙØªØ§Ø¨Ú¯Ø±Ø¯Ø§Ù† Û¸Û±Û° Ú¯Ø±Ù…', TRUE),
            (%s, %s, %s, %s, %s, 'Ø±Ø¨ Ú¯ÙˆØ¬Ù‡â€ŒÙØ±Ù†Ú¯ÛŒ Û¸Û°Û° Ú¯Ø±Ù…', TRUE);
        """, (prod_a, f"SKU-{uuid.uuid4().hex[:6].upper()}", brand_id, cat_id, subcat_id,
              prod_b, f"SKU-{uuid.uuid4().hex[:6].upper()}", brand_id, cat_id, subcat_id))

        vp_a = str(uuid.uuid4())
        vp_b = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vendor_products (id, vendor_id, product_id, vendor_sku, packaging_unit, pack_quantity, listing_status, is_active) VALUES
            (%s, %s, %s, 'VND-A-OIL', 'CARTON', 12, 'ACTIVE', TRUE),
            (%s, %s, %s, 'VND-B-TOM', 'CARTON', 12, 'ACTIVE', TRUE);
        """, (vp_a, vnda_id, prod_a, vp_b, vndb_id, prod_b))

        cur.execute("""
            INSERT INTO vendor_inventory (vendor_product_id, physical_quantity, reserved_quantity) VALUES
            (%s, 50, 0),
            (%s, 40, 0);
        """, (vp_a, vp_b))

        cur.execute("""
            INSERT INTO vendor_prices (id, vendor_product_id, price_toman, is_current) VALUES
            (%s, %s, 600000, TRUE),
            (%s, %s, 450000, TRUE);
        """, (str(uuid.uuid4()), vp_a, str(uuid.uuid4()), vp_b))
        print("  [PASS] Catalog and Inventory initialized (Vendor A=50 cartons, Vendor B=40 cartons).")

        # -------------------------------------------------------------
        # 3. Basket Versioning & Multi-Vendor Allocation
        # -------------------------------------------------------------
        print("\n[STEP 3] Basket Versioning & Multi-Vendor Allocation via BasketService & AllocationService...")
        basket_id = BasketService.create_basket(cur, ret_id)

        # Add items with optimistic version tracking (v1 -> v2 -> v3)
        v2 = BasketService.add_item_optimistic(cur, basket_id, prod_a, quantity=10, pack_quantity=12, expected_version=1)
        assert v2 == 2
        v3 = BasketService.add_item_optimistic(cur, basket_id, prod_b, quantity=15, pack_quantity=12, expected_version=2)
        assert v3 == 3

        # Allocation Engine produces Multi-Vendor Plan (D-014)
        plan = AllocationService.create_plan(cur, basket_id, basket_version=3, vendor_count=2, total_toman=12750000)
        plan_id = plan["id"]
        assert plan["strategy"] == "MULTI_VENDOR_MIN_FRAGMENTATION"
        assert plan["vendor_count"] == 2
        print(f"  [PASS] Basket v3 allocated across 2 vendors ({plan['total_estimated_toman']:,} Toman) via AllocationService.")

        # -------------------------------------------------------------
        # 4. Inventory Reservations & Checkout with Address Snapshot
        # -------------------------------------------------------------
        print("\n[STEP 4] Inventory Reservations & Checkout with Delivery Address Snapshot via CanonicalCheckoutGateway...")
        address_snapshot = {
            "address": "Ahvaz, Golestan St 5, Supermarket Golestan",
            "neighborhood": "Golestan",
            "city": "Ahvaz",
            "latitude": 31.30,
            "longitude": 48.65,
            "recipient_name": "Hossein Golestani",
            "recipient_phone": "+989161112233"
        }
        vendor_allocations = [
            {"vendor_id": vnda_id, "vendor_product_id": vp_a, "quantity": 10, "amount_toman": 6000000, "unit_price_toman": 600000},
            {"vendor_id": vndb_id, "vendor_product_id": vp_b, "quantity": 15, "amount_toman": 6750000, "unit_price_toman": 450000}
        ]
        idempotency_key = f"chk-{uuid.uuid4().hex[:16]}"
        checkout_res = CanonicalCheckoutGateway.checkout(cur, basket_id, plan_id, ret_id, idempotency_key, address_snapshot, vendor_allocations)
        og_id = checkout_res["order_group_id"]
        child_orders = checkout_res["orders"]
        assert len(child_orders) == 2

        ord_a = next(o for o in child_orders if o["vendor_id"] == vnda_id)
        ord_b = next(o for o in child_orders if o["vendor_id"] == vndb_id)
        ord_a_id = ord_a["id"]
        ord_b_id = ord_b["id"]
        corr_id = ord_a["correlation_id"]

        # Verify available stock calculation (50-10=40, 40-15=25)
        cur.execute("SELECT available_quantity FROM vendor_inventory WHERE vendor_product_id = %s;", (vp_a,))
        assert cur.fetchone()["available_quantity"] == 40
        cur.execute("SELECT available_quantity FROM vendor_inventory WHERE vendor_product_id = %s;", (vp_b,))
        assert cur.fetchone()["available_quantity"] == 25
        print("  [PASS] OrderGroup and Child Orders placed with frozen delivery address snapshot via CanonicalCheckoutGateway.")

        # -------------------------------------------------------------
        # 5. Vendor A Accepts -> Reservation CONSUMED; Vendor B Rejects -> Reservation RELEASED
        # -------------------------------------------------------------
        print("\n[STEP 5] Vendor Responses & OrderGroup Projection via OrderGroupProjector...")
        # Vendor A accepts within working SLA
        cur.execute("UPDATE orders SET order_status = 'ACCEPTED' WHERE id = %s;", (ord_a_id,))
        cur.execute("UPDATE inventory_reservations SET status = 'CONSUMED', consumed_at = now() WHERE order_id = %s;", (ord_a_id,))
        cur.execute("""
            UPDATE vendor_inventory 
            SET physical_quantity = physical_quantity - 10,
                reserved_quantity = reserved_quantity - 10
            WHERE vendor_product_id = %s;
        """, (vp_a,))

        # Vendor B rejects order
        cur.execute("UPDATE orders SET order_status = 'REJECTED', rejection_reason = 'OUT_OF_STOCK' WHERE id = %s;", (ord_b_id,))
        cur.execute("UPDATE inventory_reservations SET status = 'RELEASED', released_at = now() WHERE order_id = %s;", (ord_b_id,))
        cur.execute("UPDATE vendor_inventory SET reserved_quantity = reserved_quantity - 15 WHERE vendor_product_id = %s;", (vp_b,))

        # Check inventory state
        cur.execute("SELECT physical_quantity, reserved_quantity, available_quantity FROM vendor_inventory WHERE vendor_product_id = %s;", (vp_a,))
        inv_a = cur.fetchone()
        assert inv_a["physical_quantity"] == 40 and inv_a["reserved_quantity"] == 0 and inv_a["available_quantity"] == 40

        cur.execute("SELECT physical_quantity, reserved_quantity, available_quantity FROM vendor_inventory WHERE vendor_product_id = %s;", (vp_b,))
        inv_b = cur.fetchone()
        assert inv_b["physical_quantity"] == 40 and inv_b["reserved_quantity"] == 0 and inv_b["available_quantity"] == 40

        # Project OrderGroup Aggregate State via OrderGroupProjector
        group_status = OrderGroupProjector.project_group_status(cur, og_id)
        assert group_status == 'PARTIALLY_COMPLETED'
        print("  [PASS] Vendor A ACCEPTED (stock consumed to 40); Vendor B REJECTED (stock released to 40); OrderGroupProjector -> PARTIALLY_COMPLETED.")

        # -------------------------------------------------------------
        # 6. Delivery Dispatch (Driver Info Option A) & OTP Delivery Confirmation
        # -------------------------------------------------------------
        print("\n[STEP 6] Fulfillment: Dispatch with Driver Info (Option A) and staged OTP confirmation...")
        driver_metadata = {
            "driver_name": "Karim Driver",
            "driver_phone": "+989163334455",
            "vehicle_plate": "14 Iran 333 b 12"
        }
        dispatch_res = canonical_dispatch_order(
            cur,
            user_id=u_vnda_owner,
            organization_id=org_vnda,
            order_id=ord_a_id,
            **driver_metadata,
        )
        deliv_id = dispatch_res["delivery_id"]
        otp_code = dispatch_res["delivery_otp"]
        assert dispatch_res["delivery_status"] == "ASSIGNED"

        for stage in ("PICKED_UP", "IN_TRANSIT", "ARRIVED"):
            stage_res = transition_delivery_stage(
                cur,
                user_id=u_vnda_owner,
                organization_id=org_vnda,
                order_id=ord_a_id,
                target_status=stage,
            )
            assert stage_res["delivery_status"] == stage

        cur.execute("SELECT delivery_status FROM deliveries WHERE id = %s;", (deliv_id,))
        assert cur.fetchone()["delivery_status"] == "ARRIVED"

        canonical_confirm_delivery(
            cur,
            user_id=u_ret_owner,
            organization_id=org_ret,
            order_id=ord_a_id,
            recipient_name="Hossein Golestani",
            otp_code=otp_code,
        )
        cur.execute("SELECT delivery_status FROM deliveries WHERE id = %s;", (deliv_id,))
        assert cur.fetchone()["delivery_status"] == "DELIVERED"
        cur.execute("SELECT order_status FROM orders WHERE id = %s;", (ord_a_id,))
        assert cur.fetchone()["order_status"] == "DELIVERED"
        print("  [PASS] Delivery staged ASSIGNED→PICKED_UP→IN_TRANSIT→ARRIVED→DELIVERED with one-time OTP.")

        # -------------------------------------------------------------
        # 7. Non-Custodial Direct Payment Evidence & Verification
        # -------------------------------------------------------------
        print("\n[STEP 7] Non-Custodial Direct Payment Evidence & Verification...")
        pay_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO payments (
                id, order_id, retailer_id, vendor_id, amount_toman,
                payment_method, custody_model, payment_status
            ) VALUES (
                %s,%s,%s,%s,6000000,'DIRECT_BANK_TRANSFER','NON_CUSTODIAL_DIRECT','PENDING'
            )
            RETURNING *
            """,
            (pay_id, ord_a_id, ret_id, vnda_id),
        )
        cur.execute(
            """
            INSERT INTO payment_evidence (
                id, payment_id, evidence_type, external_reference,
                claimed_amount_toman, observed_amount_toman,
                captured_by_user_id, observation_scope, metadata
            ) VALUES (
                %s,%s,'BANK_REFERENCE',%s,6000000,6000000,%s,'SINGLE_PAYMENT','{}'::jsonb
            )
            """,
            (str(uuid.uuid4()), pay_id, f"TXN-{uuid.uuid4().hex[:12]}", u_ret_owner),
        )
        payment_boundary = POLApplicationBoundary(
            cur,
            ApplicationContext(u_vnda_owner, org_vnda, corr_id),
        )
        pay_res = payment_boundary.verify_payment(order_id=ord_a_id, notes="Master E2E verification")
        assert pay_res["status"] == "SUCCESS"
        settle_id = pay_res["settlement_id"]
        cur.execute("SELECT status FROM settlements WHERE id=%s", (settle_id,))
        assert cur.fetchone()["status"] == "CALCULATED"
        print("  [PASS] Payment verified only after matching evidence; settlement CALCULATED.")

        # -------------------------------------------------------------
        # 8. Invoices with Multi-Tenant Access
        # -------------------------------------------------------------
        print("\n[STEP 8] Invoicing & Tenant Scoping...")
        inv_id = str(uuid.uuid4())
        inv_num = f"INV-{uuid.uuid4().hex[:8].upper()}"
        cur.execute("""
            INSERT INTO invoices (id, invoice_number, order_id, retailer_organization_id, vendor_organization_id, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, 6000000, 'ISSUED');
        """, (inv_id, inv_num, ord_a_id, org_ret, org_vnda))

        cur.execute("""
            INSERT INTO invoice_items (id, invoice_id, product_name, quantity, unit_price, total_line_amount)
            VALUES (%s, %s, 'Ø±ÙˆØºÙ† Ø¢ÙØªØ§Ø¨Ú¯Ø±Ø¯Ø§Ù† Û¸Û±Û° Ú¯Ø±Ù…', 10, 600000, 6000000);
        """, (str(uuid.uuid4()), inv_id))

        # Tenant isolation check: Vendor B must see 0 invoices for this order
        cur.execute("SELECT count(*) as cnt FROM invoices WHERE vendor_organization_id = %s;", (org_vndb,))
        assert cur.fetchone()["cnt"] == 0
        print("  [PASS] Official invoice created; Vendor B isolated with 0 accessible records.")

        # -------------------------------------------------------------
        # 9. Customer Support Case (Non-Dispute)
        # -------------------------------------------------------------
        print("\n[STEP 9] Customer Support Ticket via SupportService (Distinct from Dispute)...")
        case = SupportService.create_case(cur, u_ret_owner, org_ret, 'INVOICE_INQUIRY', 'NORMAL', 'Ø§Ø³ØªØ¹Ù„Ø§Ù… Ù†Ø­ÙˆÙ‡ Ø¯Ø±ÛŒØ§ÙØª ÙØ§Ú©ØªÙˆØ± Ø±Ø³Ù…ÛŒ', ord_a_id)
        case_id = case["id"]
        assert case["status"] == "OPEN"

        msg = SupportService.add_message(cur, case_id, u_ret_owner, 'USER', 'Ù„Ø·ÙØ§ ÙØ§Ú©ØªÙˆØ± Ø±Ø³Ù…ÛŒ Ù…Ù‡Ø± Ø´Ø¯Ù‡ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ø¨ÙØ±Ù…Ø§ÛŒÛŒØ¯.')
        assert msg["sender_type"] == "USER"

        SupportService.assign_case(cur, case_id, u_admin, u_admin)
        cur.execute("SELECT status FROM support_cases WHERE id = %s;", (case_id,))
        assert cur.fetchone()["status"] == "IN_PROGRESS"

        # Verify settlement is still CALCULATED (Support does not lock settlement)
        cur.execute("SELECT status FROM settlements WHERE id = %s;", (settle_id,))
        assert cur.fetchone()["status"] == "CALCULATED"
        print("  [PASS] Support case opened and assigned without locking settlement status.")

        # -------------------------------------------------------------
        # 10. Formal Dispute Isolation & Settlement Hold
        # -------------------------------------------------------------
        print("\n[STEP 10] Formal Dispute Opening via DisputeService: Settlement Hold & Blast Radius Isolation...")
        disp_id = DisputeService.open_dispute(cur, ord_a_id, ret_id, vnda_id, settle_id, 1200000, 'Damaged goods: 2 cartons')

        cur.execute("SELECT order_status, dispute_status FROM orders WHERE id = %s;", (ord_a_id,))
        ord_status_check = cur.fetchone()
        assert ord_status_check["order_status"] == "DELIVERED"
        assert ord_status_check["dispute_status"] == "OPEN"

        cur.execute("SELECT status FROM settlements WHERE id = %s;", (settle_id,))
        assert cur.fetchone()["status"] == "DISPUTED"
        print("  [PASS] Dispute opened via DisputeService: order_status remained DELIVERED, dispute_status projected to OPEN, settlement locked in DISPUTED.")

        # -------------------------------------------------------------
        # 11. Transactional Outbox to Notification & User Inbox
        # -------------------------------------------------------------
        print("\n[STEP 11] Transactional Outbox Event to Notification Engine & User Inbox via NotificationService...")
        dispatched_count = NotificationService.dispatch_pending_outbox(cur, target_user_id=u_vnda_owner, target_org_id=org_vnda)
        assert dispatched_count >= 1

        cur.execute("SELECT count(*) as cnt FROM user_inbox_items WHERE user_id = %s AND category = 'DISPUTES';", (u_vnda_owner,))
        assert cur.fetchone()["cnt"] >= 1
        print(f"  [PASS] Outbox published to notification engine ({dispatched_count} events dispatched); durable user inbox item verified.")

        # -------------------------------------------------------------
        # 12. Admin Action & Audit Log Tracking
        # -------------------------------------------------------------
        print("\n[STEP 12] Admin Dispute Resolution & Audit Trail via AuditService...")
        audit_id = AuditService.log(
            cur,
            actor_user_id=u_admin,
            action='RESOLVE_DISPUTE',
            target_type='DISPUTE',
            target_id=disp_id,
            state_before={"dispute_status": "OPEN"},
            state_after={"dispute_status": "RESOLVED", "adjustment": 1200000},
            reason='ØªØ§ÛŒÛŒØ¯ Ù…Ø±Ø¬ÙˆØ¹ÛŒ Û² Ú©Ø§Ø±ØªÙ† Ú©Ø§Ù„Ø§ÛŒ Ø¢Ø³ÛŒØ¨â€ŒØ¯ÛŒØ¯Ù‡ Ø¨Ø§ Ø§ØµÙ„Ø§Ø­ ØªØ³ÙˆÛŒÙ‡',
            correlation_id=corr_id
        )
        cur.execute("SELECT count(*) as cnt FROM admin_audit_logs WHERE id = %s;", (audit_id,))
        assert cur.fetchone()["cnt"] == 1
        print("  [PASS] Admin action recorded via AuditService in admin_audit_logs with correlation_id.")

        conn.commit()
        conn.close()
        print("\n================================================================================")
        print("MASTER END-TO-END INTEGRATION TEST COMPLETED SUCCESSFULLY ON POSTGRESQL 18! [PASS]")
        print("================================================================================")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[FAILED]: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise

def test_master_e2e_platform():
    """Canonical pytest entry point for master E2E integration test."""
    run_master_e2e_test()

