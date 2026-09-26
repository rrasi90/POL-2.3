#!/usr/bin/env python3
"""Integration coverage for the MVP Vendor Referral loop."""

import uuid

import pytest
from psycopg2.extras import RealDictCursor

from scripts.canonical_integration_worker import CanonicalIntegrationWorker
from scripts.migration_runner import get_connection
from scripts.vendor_referral import VendorReferralAccessError, VendorReferralService


def _conn():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    return conn


def _user(cur, user_id, phone, role, name):
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,%s,%s)",
        (user_id, phone, name, role),
    )


def test_vendor_can_create_and_retailer_can_redeem_once():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        vendor_org, retailer_org = str(uuid.uuid4()), str(uuid.uuid4())
        vendor_user, retailer_user = str(uuid.uuid4()), str(uuid.uuid4())
        vendor_id, retailer_id = str(uuid.uuid4()), str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO organizations (id,name,org_type,status) VALUES
            (%s,'Referral Vendor','VENDOR','ACTIVE'),
            (%s,'Referral Retailer','RETAILER','ACTIVE')
            """,
            (vendor_org, retailer_org),
        )
        _user(cur, vendor_user, f"+98915{uuid.uuid4().int % 10000000:07d}", "VENDOR_OWNER", "Vendor")
        _user(cur, retailer_user, f"+98916{uuid.uuid4().int % 10000000:07d}", "RETAILER_OWNER", "Retailer")
        cur.execute(
            """
            INSERT INTO organization_memberships (organization_id,user_id,role,status) VALUES
            (%s,%s,'VENDOR_OWNER','ACTIVE'),
            (%s,%s,'RETAILER_OWNER','ACTIVE')
            """,
            (vendor_org, vendor_user, retailer_org, retailer_user),
        )
        cur.execute(
            """
            INSERT INTO vendors (id,user_id,organization_id,business_name,cluster_location,warehouse_address,status)
            VALUES (%s,%s,%s,'Referral Vendor','Ahvaz Hub','Vendor Warehouse','ACTIVE')
            """,
            (vendor_id, vendor_user, vendor_org),
        )
        cur.execute(
            """
            INSERT INTO retailers (id,user_id,organization_id,store_name,city,neighborhood,address)
            VALUES (%s,%s,%s,'Referral Store','Ahvaz','Bankdaran','Retailer Address')
            """,
            (retailer_id, retailer_user, retailer_org),
        )

        referral = VendorReferralService.create_referral(cur, vendor_user, vendor_id, max_redemptions=1)
        assert referral["status"] == "ACTIVE"
        assert referral["referral_code"].startswith("POLV-")

        attribution = VendorReferralService.redeem_referral(
            cur, retailer_user, retailer_id, referral["referral_code"], "referral-req-001"
        )
        assert attribution["status"] == "ATTRIBUTED"
        assert str(attribution["vendor_id"]) == vendor_id

        same = VendorReferralService.redeem_referral(
            cur, retailer_user, retailer_id, referral["referral_code"], "referral-req-002"
        )
        assert str(same["id"]) == str(attribution["id"])

        cur.execute("SELECT redemption_count FROM vendor_referrals WHERE id=%s", (referral["id"],))
        assert cur.fetchone()["redemption_count"] == 1

        cur.execute(
            "SELECT event_name,dedupe_key,target_user_id,target_organization_id,status FROM outbox_events WHERE event_id=%s",
            (f"vendor_referral_redeemed:{attribution['id']}",),
        )
        event = cur.fetchone()
        assert event["event_name"] == "VENDOR_REFERRAL_REDEEMED"
        assert event["target_user_id"] is None
        assert str(event["target_organization_id"]) == vendor_org

        # The worker drains the shared outbox oldest-first, so a single generic
        # pass can starve this test's event behind unrelated pending rows.
        # Loop until THIS referral event reaches PUBLISHED (bounded attempts).
        referral_event_id = f"vendor_referral_redeemed:{attribution['id']}"
        for _ in range(10):
            cur.execute(
                "SELECT status FROM outbox_events WHERE event_id=%s",
                (referral_event_id,),
            )
            if cur.fetchone()["status"] == "PUBLISHED":
                break
            CanonicalIntegrationWorker.process_pending(cur, limit=100)
        cur.execute(
            "SELECT status FROM outbox_events WHERE event_id=%s",
            (referral_event_id,),
        )
        assert cur.fetchone()["status"] == "PUBLISHED"
    finally:
        conn.rollback()
        conn.close()


def test_vendor_referral_is_tenant_scoped():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        vendor_org, retailer_org = str(uuid.uuid4()), str(uuid.uuid4())
        vendor_user, retailer_user = str(uuid.uuid4()), str(uuid.uuid4())
        vendor_id, retailer_id = str(uuid.uuid4()), str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO organizations (id,name,org_type,status) VALUES
            (%s,'Scoped Vendor','VENDOR','ACTIVE'),
            (%s,'Scoped Retailer','RETAILER','ACTIVE')
            """,
            (vendor_org, retailer_org),
        )
        _user(cur, vendor_user, f"+98917{uuid.uuid4().int % 10000000:07d}", "VENDOR_OWNER", "Vendor")
        _user(cur, retailer_user, f"+98918{uuid.uuid4().int % 10000000:07d}", "RETAILER_OWNER", "Retailer")
        cur.execute(
            """
            INSERT INTO organization_memberships (organization_id,user_id,role,status) VALUES
            (%s,%s,'VENDOR_OWNER','ACTIVE'),
            (%s,%s,'RETAILER_OWNER','ACTIVE')
            """,
            (vendor_org, vendor_user, retailer_org, retailer_user),
        )
        cur.execute(
            """
            INSERT INTO vendors (id,user_id,organization_id,business_name,cluster_location,warehouse_address,status)
            VALUES (%s,%s,%s,'Scoped Vendor','Ahvaz Hub','Vendor Warehouse','ACTIVE')
            """,
            (vendor_id, vendor_user, vendor_org),
        )
        cur.execute(
            """
            INSERT INTO retailers (id,user_id,organization_id,store_name,city,neighborhood,address)
            VALUES (%s,%s,%s,'Scoped Store','Ahvaz','Bankdaran','Retailer Address')
            """,
            (retailer_id, retailer_user, retailer_org),
        )
        referral = VendorReferralService.create_referral(cur, vendor_user, vendor_id)
        with pytest.raises(VendorReferralAccessError):
            VendorReferralService.redeem_referral(cur, vendor_user, retailer_id, referral["referral_code"], "bad-req")
    finally:
        conn.rollback()
        conn.close()
