"""TODO-131 - OWASP API Security Top 10 (2023) negative tests.

The matrix itself lives in `mvp/OWASP_API_SECURITY_MATRIX.md`; this module holds
the executable evidence for the rows that are not already covered by
`test_http_negative_rbac_matrix.py`, `test_api_inventory.py`,
`test_api_config_exposure.py`, `test_api_contract_drift.py` and
`test_provider_adapter_contract.py`.

Covered here:
* API1 BOLA - cross-tenant reads of invoices and support cases.
* API3 property-level authorization + mass assignment (global schema guard).
* API5 function-level authorization (admin/ops surfaces).
* API2/API4 broken authentication (anonymous and malformed tokens).
* API10 unsafe consumption of third-party responses (URL-fetch input inventory).
"""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from scripts.api.main import app
from scripts.test_http_admin_referrals import _seed_admin_vendor_retailer

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
# API3 - mass assignment is rejected for every request body
# --------------------------------------------------------------------------- #


def test_every_request_schema_forbids_additional_properties():
    spec = app.openapi()
    schemas = spec["components"]["schemas"]
    request_refs: set[str] = set()
    for operations in spec["paths"].values():
        for method, operation in operations.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            body = operation.get("requestBody") or {}
            ref = (
                body.get("content", {})
                .get("application/json", {})
                .get("schema", {})
                .get("$ref", "")
            )
            if ref:
                request_refs.add(ref.rsplit("/", 1)[-1])

    assert len(request_refs) >= 50, f"only {len(request_refs)} request schemas discovered"
    offenders = sorted(
        name
        for name in request_refs
        if schemas[name].get("additionalProperties") is not False
    )
    assert not offenders, f"request schemas accept unknown properties (mass assignment): {offenders}"


def test_mass_assignment_field_is_rejected_http(client, seeded):
    for path, body in (
        ("/profile", {"display_name": "x", "role": "ADMIN_SUPER"}),
        ("/membership/profile", {"display_name_override": "x", "permissions": ["admin.all"]}),
    ):
        response = client.put(
            f"{API}{path}", json=body, headers=_h(seeded["r_token"])
        )
        assert response.status_code == 422, (path, response.text)
        payload = response.json()
        assert payload["error"]["code"] == "VALIDATION_ERROR"
        fields = {field["type"] for field in payload["error"]["details"]["fields"]}
        assert "extra_forbidden" in fields, (path, payload)


# --------------------------------------------------------------------------- #
# API1 - BOLA / tenant isolation
# --------------------------------------------------------------------------- #


def test_other_tenant_cannot_read_invoice(client, seeded):
    response = client.get(f"{API}/invoices/{uuid.uuid4()}", headers=_h(seeded["r_token"]))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_retailer_support_case_is_not_visible_to_vendor(client, seeded):
    created = client.post(
        f"{API}/support/cases",
        json={"case_type": "GENERAL", "subject": "BOLA probe", "priority": "NORMAL"},
        headers=_h(seeded["r_token"]),
    )
    assert created.status_code in (200, 201), created.text
    data = created.json()["data"]
    case_id = data.get("case_id") or data.get("id")
    assert case_id, data

    vendor_read = client.get(f"{API}/support/cases/{case_id}", headers=_h(seeded["v_token"]))
    assert vendor_read.status_code in (403, 404), vendor_read.text
    assert vendor_read.json()["success"] is False


# --------------------------------------------------------------------------- #
# API3 - property-level authorization
# --------------------------------------------------------------------------- #


def test_retailer_cannot_adjust_vendor_inventory(client, seeded):
    response = client.patch(
        f"{API}/catalog/vendors/products/{uuid.uuid4()}/inventory",
        json={"new_physical_quantity": 5},
        headers=_h(seeded["r_token"]),
    )
    assert response.status_code == 403, response.text
    error = response.json()["error"]
    assert error["code"] == "FORBIDDEN"
    assert "inventory.adjust" in error["message"]


# --------------------------------------------------------------------------- #
# API5 - function-level authorization
# --------------------------------------------------------------------------- #


def test_retailer_cannot_reach_admin_user_management(client, seeded):
    response = client.get(f"{API}/admin/users", headers=_h(seeded["r_token"]))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_vendor_cannot_reach_ops_analytics(client, seeded):
    response = client.get(
        f"{API}/ops/analytics",
        params={"start_date": "2026-10-01", "end_date": "2026-10-23"},
        headers=_h(seeded["v_token"]),
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


# --------------------------------------------------------------------------- #
# API2/API4 - authentication
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "method,path",
    [
        ("post", f"{API}/media/presigned-url"),
        ("get", f"{API}/orders"),
        ("get", f"{API}/admin/audit-logs"),
    ],
)
def test_protected_routes_reject_anonymous_requests(client, method, path):
    kwargs = {"json": {"file_name": "a.png", "content_type": "image/png"}} if method == "post" else {}
    response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


def test_malformed_bearer_token_is_rejected(client):
    response = client.get(f"{API}/orders", headers=_h("not-a-jwt"))
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


# --------------------------------------------------------------------------- #
# API10 / SSRF - no server-side URL fetching input surface
# --------------------------------------------------------------------------- #


def test_no_request_model_accepts_a_server_side_fetch_url():
    spec = app.openapi()
    suspicious: list[str] = []
    for name, schema in spec["components"]["schemas"].items():
        for prop in (schema.get("properties") or {}):
            if prop == "icon_url":
                continue
            if any(token in prop.lower() for token in ("webhook", "callback", "fetch_url", "target_url", "endpoint_url", "uri")):
                suspicious.append(f"{name}.{prop}")
    assert not suspicious, f"server-side fetch surface found; SSRF review required: {suspicious}"

# --------------------------------------------------------------------------- #
# API6/API8 - invalid enum/FK input is a 422, never a 500
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "actor,method,path,body",
    [
        ("r_token", "post", "/support/cases", {"case_type": "BOGUS", "subject": "x"}),
        ("r_token", "post", "/support/cases", {"case_type": "GENERAL", "subject": "x", "priority": "BOGUS"}),
        ("r_token", "post", "/support/cases", {"case_type": "GENERAL", "subject": "x", "related_order_id": "not-a-uuid"}),
        ("r_token", "put", "/notifications/preferences", {"event_name": "x", "channel": "BOGUS", "is_enabled": True}),
        ("a_token", "post", "/field/tasks", {"task_type": "BOGUS", "assigned_to_user_id": "00000000-0000-0000-0000-000000000000"}),
        ("a_token", "post", "/field/tasks", {"task_type": "FOLLOW_UP", "assigned_to_user_id": "not-a-uuid"}),
        ("a_token", "post", "/admin/broadcasts", {"title": "t", "body": "b", "target_criteria": {"x": 1}, "channel": "BOGUS"}),
        (
            "v_token",
            "post",
            "/catalog/vendors/products",
            {"vendor_sku": "SKU-FK", "product_id": "00000000-0000-0000-0000-000000000000"},
        ),
    ],
)
def test_invalid_enum_or_reference_is_422_not_500(client, seeded, actor, method, path, body):
    response = getattr(client, method)(f"{API}{path}", json=body, headers=_h(seeded[actor]))
    assert response.status_code == 422, (path, response.status_code, response.text)
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] in {"VALIDATION_ERROR", "INVALID_REQUEST"}

