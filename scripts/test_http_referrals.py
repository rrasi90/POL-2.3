"""HTTP regression coverage for the canonical Vendor Referral redemption flow."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import psycopg2
from fastapi.testclient import TestClient
from psycopg2.extras import RealDictCursor

from scripts.api.main import app
from scripts.auth_boundary import encode_access_token, hash_token


def _db():
    return psycopg2.connect(
        dbname=os.environ.get("POL_API_DB_NAME", "pol_test"),
        host=os.environ.get("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1")),
        port=int(os.environ.get("POL_API_DB_PORT", os.environ.get("PGPORT", "5432"))),
        user=os.environ.get("POL_API_DB_USER", os.environ.get("PGUSER", "postgres")),
    )


def _session(cur, user_id, organization_id):
    sid = str(uuid4())
    cur.execute(
        """
        INSERT INTO user_sessions
            (id,user_id,active_organization_id,token_hash,status,expires_at)
        VALUES (%s,%s,%s,%s,'ACTIVE',%s)
        """,
        (
            sid,
            user_id,
            organization_id,
            hash_token(sid),
            datetime.now(timezone.utc) + timedelta(hours=1),
        ),
    )
    return sid


def test_http_referral_redeem_creates_first_touch_attribution():
    conn = _db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    vendor_org = str(uuid4())
    retailer_org = str(uuid4())
    vendor_user = str(uuid4())
    retailer_user = str(uuid4())
    vendor_id = str(uuid4())
    retailer_id = str(uuid4())
    referral_id = str(uuid4())
    membership_vendor = str(uuid4())
    membership_retailer = str(uuid4())

    try:
        cur.execute(
            """
            INSERT INTO organizations (id,name,org_type,status) VALUES
            (%s,'Referral HTTP Vendor','VENDOR','ACTIVE'),
            (%s,'Referral HTTP Retailer','RETAILER','ACTIVE')
            """,
            (vendor_org, retailer_org),
        )
        cur.execute(
            """
            INSERT INTO users (id,phone_number,full_name,role) VALUES
            (%s,%s,'Referral Vendor','VENDOR_OWNER'),
            (%s,%s,'Referral Retailer','RETAILER_OWNER')
            """,
            (
                vendor_user,
                f"+9891{uuid4().int % 100000000:08d}",
                retailer_user,
                f"+9891{uuid4().int % 100000000:08d}",
            ),
        )
        cur.execute(
            """
            INSERT INTO organization_memberships
                (id,organization_id,user_id,role,status,is_primary) VALUES
            (%s,%s,%s,'VENDOR_OWNER','ACTIVE',TRUE),
            (%s,%s,%s,'RETAILER_OWNER','ACTIVE',TRUE)
            """,
            (
                membership_vendor, vendor_org, vendor_user,
                membership_retailer, retailer_org, retailer_user,
            ),
        )
        cur.execute(
            """
            INSERT INTO vendors
                (id,user_id,organization_id,business_name,warehouse_address,
                 min_order_value_toman,status)
            VALUES (%s,%s,%s,'Referral HTTP Vendor','Ahvaz Warehouse',1000000,'ACTIVE')
            """,
            (vendor_id, vendor_user, vendor_org),
        )
        cur.execute(
            """
            INSERT INTO retailers
                (id,user_id,organization_id,store_name,city,neighborhood,address)
            VALUES (%s,%s,%s,'Referral HTTP Store','Ahvaz','Bankdaran','Store Address')
            """,
            (retailer_id, retailer_user, retailer_org),
        )
        cur.execute(
            """
            INSERT INTO vendor_referrals
                (id,vendor_id,referral_code,status,max_redemptions,created_by_user_id)
            VALUES (%s,%s,'POLV-HTTP01','ACTIVE',1,%s)
            """,
            (referral_id, vendor_id, vendor_user),
        )
        sid = _session(cur, retailer_user, retailer_org)
        conn.commit()

        token = encode_access_token(
            retailer_user, sid, retailer_org, "RETAILER_OWNER"
        )
        client = TestClient(app, raise_server_exceptions=False)

        first = client.post(
            f"/api/v1/referrals/{referral_id}/redeem",
            headers={"Authorization": f"Bearer {token}"},
            json={},
        )
        assert first.status_code == 200
        body = first.json()
        assert body["success"] is True
        assert body["data"]["status"] == "ATTRIBUTED"
        attribution_id = body["data"]["id"]

        second = client.post(
            f"/api/v1/referrals/{referral_id}/redeem",
            headers={"Authorization": f"Bearer {token}"},
            json={},
        )
        assert second.status_code == 200
        second_body = second.json()
        assert second_body["success"] is True
        assert second_body["data"]["id"] == attribution_id

        cur.execute(
            """
            SELECT redemption_count
            FROM vendor_referrals
            WHERE id=%s
            """,
            (referral_id,),
        )
        assert int(cur.fetchone()["redemption_count"]) == 1

        cur.execute(
            """
            SELECT referral_id,vendor_id,retailer_id,status
            FROM vendor_referral_attributions
            WHERE id=%s
            """,
            (attribution_id,),
        )
        attribution = cur.fetchone()
        assert str(attribution["referral_id"]) == referral_id
        assert str(attribution["vendor_id"]) == vendor_id
        assert str(attribution["retailer_id"]) == retailer_id
        assert attribution["status"] == "ATTRIBUTED"
    finally:
        conn.rollback()
        cur.close()
        conn.close()
