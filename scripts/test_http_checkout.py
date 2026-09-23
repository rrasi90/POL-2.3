"""HTTP transport tests for the canonical checkout route."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from scripts.api.dependencies import get_application_boundary
from scripts.api.main import app


@pytest.fixture
def api_test_environment(monkeypatch):
    pg_port = (
        os.environ.get("POL_API_DB_PORT")
        or os.environ.get("POL_PG_PORT")
        or os.environ.get("PGPORT")
        or "5432"
    )
    monkeypatch.setenv("POL_API_DB_NAME", "pol_test")
    monkeypatch.setenv("POL_API_DB_HOST", os.environ.get("PGHOST", "127.0.0.1"))
    monkeypatch.setenv("POL_API_DB_PORT", pg_port)
    monkeypatch.setenv("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")
    monkeypatch.setenv("ENVIRONMENT", "test")



class _FakeBoundary:
    def checkout_from_allocation_plan(
        self,
        *,
        allocation_plan_id,
        delivery_address,
        preferred_payment_method,
        idempotency_key,
    ):
        return {
            "order_group_id": allocation_plan_id,
            "group_status": "ACTIVE",
            "total_amount_toman": 14000000,
            "child_orders": [
                {
                    "order_id": str(uuid4()),
                    "vendor_id": str(uuid4()),
                    "order_status": "SUBMITTED",
                    "subtotal_toman": 14000000,
                }
            ],
            "idempotent_replay": False,
        }


@pytest.fixture
def client(monkeypatch):
    from scripts.api.dependencies import (
        get_application_boundary,
        get_application_context,
    )
    from scripts.application_boundary import ApplicationContext
    from scripts.domain_services import AuthService

    monkeypatch.setattr(
        AuthService,
        "authorize_action",
        lambda *a, **k: {"role": "VENDOR_OWNER", "status": "ACTIVE", "org_type": "VENDOR"},
    )
    app.dependency_overrides[get_application_boundary] = lambda: _FakeBoundary()
    app.dependency_overrides[get_application_context] = lambda: ApplicationContext(
        user_id="http-contract-user",
        organization_id="http-contract-org",
        correlation_id="http-contract-corr",
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_checkout_route_returns_canonical_order_contract(client):
    plan_id = uuid4()
    response = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": str(uuid4())},
        json={
            "allocation_plan_id": str(plan_id),
            "delivery_address": "Ahvaz, Naderi, Test Street 1",
            "preferred_payment_method": "POS_DRIVER",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["order_group_id"] == str(plan_id)
    assert body["data"]["group_status"] == "ACTIVE"


def test_checkout_requires_uuid4_idempotency_key(client):
    valid = str(uuid4())
    invalid = valid[:14] + "7" + valid[15:]
    response = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": invalid},
        json={
            "allocation_plan_id": str(uuid4()),
            "delivery_address": "Ahvaz, Naderi, Test Street 1",
            "preferred_payment_method": "POS_DRIVER",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


def test_checkout_requires_idempotency_header(client):
    response = client.post(
        "/api/v1/orders",
        json={
            "allocation_plan_id": str(uuid4()),
            "delivery_address": "Ahvaz, Naderi, Test Street 1",
            "preferred_payment_method": "POS_DRIVER",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_checkout_rejects_extra_request_fields(client):
    response = client.post(
        "/api/v1/orders",
        headers={"Idempotency-Key": str(uuid4())},
        json={
            "allocation_plan_id": str(uuid4()),
            "delivery_address": "Ahvaz, Naderi, Test Street 1",
            "preferred_payment_method": "POS_DRIVER",
            "retailer_id": str(uuid4()),
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_checkout_transport_source_boundary_has_no_domain_import_or_sql():
    from pathlib import Path

    route_text = (
        Path(__file__).resolve().parents[0] / "api" / "routes" / "orders.py"
    ).read_text(encoding="utf-8")

    assert "domain_services" not in route_text
    assert "SELECT " not in route_text
    assert "INSERT " not in route_text
    assert "UPDATE " not in route_text
    assert "DELETE " not in route_text


def test_checkout_route_is_auth_protected(api_test_environment):
    app.dependency_overrides.clear()
    response = TestClient(app).post(
        "/api/v1/orders",
        headers={"Idempotency-Key": str(uuid4())},
        json={
            "allocation_plan_id": str(uuid4()),
            "delivery_address": "Ahvaz, Naderi, Test Street 1",
            "preferred_payment_method": "POS_DRIVER",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"
