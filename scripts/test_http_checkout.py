"""HTTP transport tests for the canonical checkout route."""

from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from scripts.api.dependencies import get_application_boundary
from scripts.api.main import app


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
def client():
    app.dependency_overrides[get_application_boundary] = lambda: _FakeBoundary()
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


def test_checkout_route_is_auth_protected():
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
