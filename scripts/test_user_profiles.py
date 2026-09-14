#!/usr/bin/env python3
"""Verification suite for canonical user profiles and persona contexts."""

import uuid

import pytest
from psycopg2.extras import RealDictCursor

from scripts.migration_runner import get_connection
from scripts.application_boundary import ApplicationContext, POLApplicationBoundary
from scripts.user_profiles import UserProfileService


def _conn():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    return conn


def _user(cur, role, name):
    user_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,%s,%s)",
        (user_id, f"+9891{uuid.uuid4().int % 100000000:08d}", name, role),
    )
    return user_id


def test_every_user_gets_exactly_one_profile():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        user_id = _user(cur, "RETAILER_OWNER", "Profile User")
        cur.execute("SELECT COUNT(*) AS c FROM user_profiles WHERE user_id=%s", (user_id,))
        assert cur.fetchone()["c"] == 1
        cur.execute("SELECT display_name FROM user_profiles WHERE user_id=%s", (user_id,))
        assert cur.fetchone()["display_name"] == "Profile User"
    finally:
        conn.rollback()
        conn.close()


def test_membership_gets_role_specific_persona_profile():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        vendor_org = str(uuid.uuid4())
        retailer_org = str(uuid.uuid4())
        vendor_user = _user(cur, "VENDOR_OWNER", "Vendor Owner")
        retailer_user = _user(cur, "RETAILER_OWNER", "Retailer Owner")
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'VP','VENDOR','ACTIVE'),(%s,'RP','RETAILER','ACTIVE')",
            (vendor_org, retailer_org),
        )
        cur.execute(
            """INSERT INTO organization_memberships (id,organization_id,user_id,role,status)
               VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE'),(%s,%s,%s,'RETAILER_OWNER','ACTIVE')
            """,
            (str(uuid.uuid4()), vendor_org, vendor_user, str(uuid.uuid4()), retailer_org, retailer_user),
        )
        cur.execute(
            """SELECT vmp.can_create_referrals, mp.preferred_dashboard
               FROM vendor_membership_profiles vmp
               JOIN membership_profiles mp ON mp.membership_id=vmp.membership_id
               JOIN organization_memberships m ON m.id=vmp.membership_id
               WHERE m.user_id=%s""",
            (vendor_user,),
        )
        vendor = cur.fetchone()
        assert vendor["can_create_referrals"] is True
        assert vendor["preferred_dashboard"] == "VENDOR_HOME"

        cur.execute(
            """SELECT rmp.store_role, mp.preferred_dashboard
               FROM retailer_membership_profiles rmp
               JOIN membership_profiles mp ON mp.membership_id=rmp.membership_id
               JOIN organization_memberships m ON m.id=rmp.membership_id
               WHERE m.user_id=%s""",
            (retailer_user,),
        )
        retailer = cur.fetchone()
        assert retailer["store_role"] == "OWNER"
        assert retailer["preferred_dashboard"] == "RETAILER_HOME"
    finally:
        conn.rollback()
        conn.close()


def test_profile_is_tenant_scoped_and_personal_update_does_not_cross_tenant():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org_a, org_b = str(uuid.uuid4()), str(uuid.uuid4())
        user = _user(cur, "VENDOR_OWNER", "Multi Tenant User")
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'A','VENDOR','ACTIVE'),(%s,'B','VENDOR','ACTIVE')",
            (org_a, org_b),
        )
        cur.execute(
            """INSERT INTO organization_memberships (organization_id,user_id,role,status,is_primary)
               VALUES (%s,%s,'VENDOR_OWNER','ACTIVE',TRUE),(%s,%s,'VENDOR_OWNER','ACTIVE',FALSE)""",
            (org_a, user, org_b, user),
        )
        UserProfileService.update_my_profile(cur, user, {"display_name": "Updated Name", "preferred_language": "fa-IR"})
        a = UserProfileService.get_my_profile(cur, user, org_a)
        b = UserProfileService.get_my_profile(cur, user, org_b)
        assert a["user_profile"]["display_name"] == "Updated Name"
        assert b["user_profile"]["display_name"] == "Updated Name"
        assert str(a["membership"]["organization_id"]) == org_a
        assert str(b["membership"]["organization_id"]) == org_b
    finally:
        conn.rollback()
        conn.close()


def test_profile_application_boundary_routes_only_to_current_user():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org = str(uuid.uuid4())
        user = _user(cur, "VENDOR_OWNER", "Boundary User")
        cur.execute("INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'B','VENDOR','ACTIVE')", (org,))
        cur.execute(
            "INSERT INTO organization_memberships (organization_id,user_id,role,status) VALUES (%s,%s,'VENDOR_OWNER','ACTIVE')",
            (org, user),
        )
        boundary = POLApplicationBoundary(cur, ApplicationContext(user, org, "corr-profile"))
        boundary.profile_update(fields={"bio": "Warehouse owner"})
        profile = boundary.profile_get()
        assert profile["user_profile"]["bio"] == "Warehouse owner"
        assert profile["membership_profile"]["preferred_dashboard"] == "VENDOR_HOME"
        assert profile["persona_profile"]["can_create_referrals"] is True
    finally:
        conn.rollback()
        conn.close()


def test_role_transition_removes_stale_persona_context():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        org_vendor = str(uuid.uuid4())
        org_operator = str(uuid.uuid4())
        user = _user(cur, "VENDOR_OWNER", "Transition User")
        cur.execute(
            "INSERT INTO organizations (id,name,org_type,status) VALUES (%s,'V','VENDOR','ACTIVE'),(%s,'O','OPERATOR','ACTIVE')",
            (org_vendor, org_operator),
        )
        membership = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO organization_memberships (id,organization_id,user_id,role,status) VALUES (%s,%s,%s,'VENDOR_OWNER','ACTIVE')",
            (membership, org_vendor, user),
        )
        cur.execute(
            "UPDATE organization_memberships SET organization_id=%s, role='OPS_AGENT' WHERE id=%s",
            (org_operator, membership),
        )
        cur.execute("SELECT COUNT(*) AS c FROM vendor_membership_profiles WHERE membership_id=%s", (membership,))
        assert cur.fetchone()["c"] == 0
        cur.execute("SELECT COUNT(*) AS c FROM operator_membership_profiles WHERE membership_id=%s", (membership,))
        assert cur.fetchone()["c"] == 1
    finally:
        conn.rollback()
        conn.close()
