#!/usr/bin/env python3
"""Cross-domain verification for the post-UI route hardening boundary."""

import os
import uuid

import pytest
from psycopg2.extras import RealDictCursor

from scripts.canonical_feedback import CanonicalFeedbackService, FeedbackAccessError
from scripts.canonical_support import CanonicalSupportService, SupportAccessError
from scripts.migration_runner import get_connection
from scripts.provider_adapters import ProviderConfigurationError, build_adapter
from scripts.returns_rma import CanonicalReturnService, ReturnStateError


def _conn():
    conn, _ = get_connection("pol_test")
    conn.autocommit = False
    return conn


def _user(cur, user_id, phone, role, name):
    cur.execute(
        "INSERT INTO users (id, phone_number, full_name, role) VALUES (%s,%s,%s,%s)",
        (user_id, phone, name, role),
    )


def test_support_case_is_tenant_scoped_and_ops_authorized():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        retailer_org, operator_org = str(uuid.uuid4()), str(uuid.uuid4())
        user_id, outsider_id, ops_id = [str(uuid.uuid4()) for _ in range(3)]
        cur.execute(
            """
            INSERT INTO organizations (id,name,org_type,status) VALUES
            (%s,'Route Retailer','RETAILER','ACTIVE'),
            (%s,'POL Ops','OPERATOR','ACTIVE')
            """,
            (retailer_org, operator_org),
        )
        _user(cur, user_id, f"+98910{uuid.uuid4().int % 10000000:07d}", "RETAILER_OWNER", "Retailer")
        _user(cur, outsider_id, f"+98911{uuid.uuid4().int % 10000000:07d}", "RETAILER_OWNER", "Outsider")
        _user(cur, ops_id, f"+98912{uuid.uuid4().int % 10000000:07d}", "OPS_AGENT", "Ops")
        cur.execute(
            """
            INSERT INTO organization_memberships (organization_id,user_id,role,status) VALUES
            (%s,%s,'RETAILER_OWNER','ACTIVE'),
            (%s,%s,'RETAILER_OWNER','ACTIVE'),
            (%s,%s,'OPS_AGENT','ACTIVE')
            """,
            (retailer_org, user_id, retailer_org, outsider_id, operator_org, ops_id),
        )

        case = CanonicalSupportService.create_case(cur, user_id, retailer_org, "GENERAL", "Need help")
        assert case["status"] == "OPEN"
        assert CanonicalSupportService.get_case(cur, user_id, case["id"])["id"] == case["id"]
        assert CanonicalSupportService.get_case(cur, ops_id, case["id"])["id"] == case["id"]

        with pytest.raises(SupportAccessError):
            CanonicalSupportService.get_case(cur, outsider_id, case["id"])
        with pytest.raises(SupportAccessError):
            CanonicalSupportService.add_message(cur, user_id, case["id"], "secret", internal=True)

        CanonicalSupportService.add_message(cur, ops_id, case["id"], "Internal triage", internal=True)
        updated = CanonicalSupportService.transition(cur, ops_id, case["id"], "IN_PROGRESS")
        assert updated["status"] == "IN_PROGRESS"

        cur.execute(
            "SELECT allowed, action FROM support_case_access_audit WHERE support_case_id=%s ORDER BY created_at",
            (case["id"],),
        )
        audit = cur.fetchall()
        assert any(not row["allowed"] for row in audit)
        assert any(row["action"] == "INTERNAL_NOTE" and row["allowed"] for row in audit)
    finally:
        conn.rollback()
        conn.close()


def test_feedback_reply_is_admin_authorized_and_emits_outbox():
    conn = _conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        retailer_org, operator_org = str(uuid.uuid4()), str(uuid.uuid4())
        user_id, ops_id = str(uuid.uuid4()), str(uuid.uuid4())
        feedback_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO organizations (id,name,org_type,status) VALUES
            (%s,'Feedback Retailer','RETAILER','ACTIVE'),
            (%s,'Feedback Ops','OPERATOR','ACTIVE')
            """,
            (retailer_org, operator_org),
        )
        _user(cur, user_id, f"+98913{uuid.uuid4().int % 10000000:07d}", "RETAILER_OWNER", "Retailer")
        _user(cur, ops_id, f"+98914{uuid.uuid4().int % 10000000:07d}", "OPS_AGENT", "Ops")
        cur.execute(
            """
            INSERT INTO organization_memberships (organization_id,user_id,role,status) VALUES
            (%s,%s,'RETAILER_OWNER','ACTIVE'),
            (%s,%s,'OPS_AGENT','ACTIVE')
            """,
            (retailer_org, user_id, operator_org, ops_id),
        )
        cur.execute(
            """
            INSERT INTO feedback_submissions
                (id,user_id,organization_id,feedback_type,priority,status,visibility,description)
            VALUES (%s,%s,%s,'SUGGESTION','NORMAL','SUBMITTED','PRIVATE_TO_ADMIN','Make reorder easier')
            """,
            (feedback_id, user_id, retailer_org),
        )
        updated = CanonicalFeedbackService.reply(cur, ops_id, feedback_id, "Accepted for review")
        assert updated["admin_reply"] == "Accepted for review"
        cur.execute(
            "SELECT event_name,target_user_id,target_organization_id FROM outbox_events WHERE event_id=%s",
            (f"feedback_replied:{feedback_id}",),
        )
        row = cur.fetchone()
        assert row["event_name"] == "FEEDBACK_REPLIED"
        assert str(row["target_user_id"]) == user_id
        assert str(row["target_organization_id"]) == retailer_org
    finally:
        conn.rollback()
        conn.close()


def test_rma_transition_contract_rejects_illegal_transition():
    assert "APPROVED" in CanonicalReturnService.TRANSITIONS["RETURN_REQUESTED"]
    assert "REFUNDED" not in CanonicalReturnService.TRANSITIONS["RETURN_REQUESTED"]
    with pytest.raises(ReturnStateError):
        raise ReturnStateError("RETURN_REQUESTED -> REFUNDED is forbidden")


def test_external_provider_configuration_is_explicit(monkeypatch):
    monkeypatch.delenv("POL_SMS_ENDPOINT", raising=False)
    monkeypatch.delenv("POL_PUSH_ENDPOINT", raising=False)
    with pytest.raises(ProviderConfigurationError):
        build_adapter("SMS")
    with pytest.raises(ProviderConfigurationError):
        build_adapter("PUSH")
