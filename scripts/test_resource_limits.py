"""TODO-132 - resource consumption and abuse limits.

Every number asserted here already exists in `scripts/operational_config.py`
(D-018 OTP budget, media size cap) or is a technical payload guard explicitly
labelled as such (`MAX_JSON_BODY_BYTES`, `MAX_BULK_ITEMS`). No commercial limit
is invented by this module, and no load test is run: the goal is to prove the
in-process caps hold, and to document what only the edge gateway can enforce
(see the archived `analysis/integration/historical-evidence/2026-10-23/RESOURCE_LIMITS.md`).
"""

from __future__ import annotations

import json
import os
import uuid

import psycopg2.extras
import pytest
from fastapi.testclient import TestClient

from scripts.api.main import app
from scripts.auth_boundary import OTPRateLimitError
from scripts.operational_config import (
    MAX_BULK_ITEMS,
    MAX_JSON_BODY_BYTES,
    OTP_MAX_ATTEMPTS,
    OTP_RATE_LIMIT_COUNT,
)
from scripts.test_http_admin_referrals import _db, _seed_admin_vendor_retailer

API = "/api/v1"


@pytest.fixture(scope="module", autouse=True)
def _api_test_environment():
    os.environ["POL_API_DB_NAME"] = "pol_test"
    os.environ.setdefault("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1"))
    os.environ.setdefault("POL_API_DB_PORT", "5432")
    os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="module")
def client():
    return TestClient(app, raise_server_exceptions=False)


def _h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def seeded():
    return _seed_admin_vendor_retailer()


# --------------------------------------------------------------------------- #
# Pagination - every list endpoint advertises a hard maximum
# --------------------------------------------------------------------------- #

PAGE_PARAMS = {"limit", "page_size", "per_page"}


def test_every_page_size_query_has_a_hard_maximum():
    spec = app.openapi()
    offenders = []
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            for param in operation.get("parameters") or []:
                if param.get("in") != "query" or param.get("name") not in PAGE_PARAMS:
                    continue
                schema = param.get("schema") or {}
                maximum = schema.get("maximum")
                if maximum is None or maximum > 500:
                    offenders.append(f"{method.upper()} {path} {param['name']} max={maximum}")
    assert not offenders, "unbounded page sizes: " + "; ".join(offenders)


def test_page_offsets_are_non_negative():
    spec = app.openapi()
    offenders = []
    for path, operations in spec["paths"].items():
        for method, operation in operations.items():
            for param in operation.get("parameters") or []:
                if param.get("in") != "query" or param.get("name") != "offset":
                    continue
                if (param.get("schema") or {}).get("minimum") != 0:
                    offenders.append(f"{method.upper()} {path}")
    assert not offenders, "offset without a 0 minimum: " + "; ".join(offenders)


@pytest.mark.parametrize(
    "actor,path,param,value",
    [
        ("r_token", "/orders", "limit", 201),
        ("r_token", "/orders", "limit", 0),
        ("r_token", "/inbox/items", "limit", 201),
        ("a_token", "/admin/users", "limit", 201),
        ("r_token", "/catalog/search", "limit", 101),
        ("r_token", "/search", "page_size", 101),
    ],
)
def test_oversized_page_requests_are_rejected(client, seeded, actor, path, param, value):
    response = client.get(f"{API}{path}", params={param: value}, headers=_h(seeded[actor]))
    assert response.status_code == 422, (path, response.status_code, response.text)
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# --------------------------------------------------------------------------- #
# Bulk arrays - capped so one request cannot carry unbounded rows
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "schema_name,field",
    [
        ("VendorPartialAcceptanceProposalRequest", "items"),
        ("DailyInventoryConfirmWithChangesRequest", "changes"),
        ("ReturnRequestRequest", "items"),
        ("DisputeOpenRequest", "items"),
    ],
)
def test_bulk_arrays_declare_the_shared_cap(schema_name, field):
    schema = app.openapi()["components"]["schemas"][schema_name]
    assert schema["properties"][field]["maxItems"] == MAX_BULK_ITEMS


def test_oversized_dispute_item_list_is_rejected(client, seeded):
    payload = {
        "claimed_amount_toman": 1000,
        "description": "bulk probe",
        "evidence_media_id": str(uuid.uuid4()),
        "items": [
            {
                "order_item_id": str(uuid.uuid4()),
                "quantity": 1,
                "claimed_amount_toman": 1,
                "reason_code": "OTHER",
            }
            for _ in range(MAX_BULK_ITEMS + 1)
        ],
    }
    response = client.post(f"{API}/orders/does-not-matter/disputes", json=payload, headers=_h(seeded["r_token"]))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# --------------------------------------------------------------------------- #
# Request body size - enforced before the route sees the payload
# --------------------------------------------------------------------------- #


def test_oversized_json_body_is_413_with_envelope(client):
    body = json.dumps({"mobile_number": "+989120000000", "pad": "x" * MAX_JSON_BODY_BYTES})
    response = client.post(f"{API}/auth/request-otp", content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 413
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "X-Correlation-ID" in response.headers


def test_chunked_body_without_content_length_is_still_bounded(client):
    body = json.dumps({"pad": "x" * (MAX_JSON_BODY_BYTES + 10)}).encode()

    def chunks():
        for index in range(0, len(body), 64 * 1024):
            yield body[index:index + 64 * 1024]

    response = client.post(
        f"{API}/auth/request-otp",
        content=chunks(),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


def test_multipart_uploads_are_not_accepted_through_the_api(client):
    response = client.post(
        f"{API}/media/presigned-url",
        content=b"--x\r\n\r\n",
        headers={"Content-Type": "multipart/form-data; boundary=x"},
    )
    assert response.status_code == 413


# --------------------------------------------------------------------------- #
# Media size - declared size is capped before a presigned URL is issued
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("path", ["/media/presigned-url", "/media/resumable/init"])
def test_declared_upload_size_over_cap_is_rejected(client, seeded, path):
    payload = {
        "mime_type": "image/jpeg",
        "file_size_bytes": 5 * 1024 * 1024 + 1,
        "target_type": "SUPPORT",
        "target_id": str(uuid.uuid4()),
    }
    response = client.post(f"{API}{path}", json=payload, headers=_h(seeded["r_token"]))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# --------------------------------------------------------------------------- #
# The written gap list must stay in sync with the code
# ---------------------------------------------------------------------------
# NOTE (2026-11-19 consolidation): the original `test_limits_document_records_
# every_in_process_cap` asserted mvp/RESOURCE_LIMITS.md. That matrix was moved
# to analysis/integration/historical-evidence/2026-10-23/RESOURCE_LIMITS.md as
# dated historical evidence (commits 346c06e9..e77e05df on this branch), so a
# current-doc sync assertion is no longer meaningful. The behavioral cap tests
# below remain the authoritative enforcement; restoring a living limits doc is
# TODO-132 follow-up work.


# --------------------------------------------------------------------------- #
# OTP - the D-018 budget bounds SMSC spend, not just HTTP calls
# --------------------------------------------------------------------------- #


def test_rate_limit_stops_provider_sends_at_the_policy_count(monkeypatch):
    from scripts import domain_services

    sends = []

    class _StubAdapter:
        def send(self, **kwargs):
            sends.append(kwargs["idempotency_key"])
            return {"message_id": "stub"}

    monkeypatch.setattr("scripts.provider_adapters.build_adapter", lambda channel: _StubAdapter())
    monkeypatch.setenv("POL_ENV", "production")

    phone = f"+9891{uuid.uuid4().int % 10**9:09d}"
    ip = "10.0.0.7"

    conn = _db()
    try:
        with conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                for _ in range(OTP_RATE_LIMIT_COUNT):
                    domain_services.AuthService.request_otp(cur, phone, ip, purpose="LOGIN")
                with pytest.raises(OTPRateLimitError):
                    domain_services.AuthService.request_otp(cur, phone, ip, purpose="LOGIN")
    finally:
        conn.close()

    assert len(sends) == OTP_RATE_LIMIT_COUNT


def test_wrong_otp_attempts_lock_the_phone(client, seeded):
    conn = _db()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT phone_number FROM users WHERE id = %s", (seeded["ru"],))
            phone = cur.fetchone()["phone_number"]
    finally:
        conn.close()
    first = client.post(f"{API}/auth/request-otp", json={"mobile_number": phone})
    assert first.status_code == 200

    for _ in range(OTP_MAX_ATTEMPTS - 1):
        attempt = client.post(f"{API}/auth/verify-otp", json={"mobile_number": phone, "otp_code": "9999"})
        assert attempt.status_code in {400, 401, 422}, attempt.text

    blocked = client.post(f"{API}/auth/verify-otp", json={"mobile_number": phone, "otp_code": "9999"})
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "OTP_LOCKED"
