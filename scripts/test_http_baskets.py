"""HTTP transport tests for the canonical basket and allocation routes."""

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
    monkeypatch.setenv(
        "POL_JWT_SECRET",
        "test-secret-key-for-auth-contract-tests-only-32bytes!!",
    )
    monkeypatch.setenv("ENVIRONMENT", "test")


class _FakeBoundary:
    def basket_create(self):
        return {"basket_id": str(uuid4()), "version": 1, "status": "OPEN"}

    def basket_add_item(
        self,
        *,
        basket_id,
        product_id,
        quantity,
        pack_quantity,
        expected_version,
    ):
        return {"basket_id": basket_id, "version": expected_version + 1, "status": "OPEN"}

    def basket_allocation_preview(self, *, basket_id):
        return {
            "allocation_plan_id": str(uuid4()),
            "strategy": "MULTI_VENDOR_MIN_FRAGMENTATION",
            "vendor_count": 1,
            "allocated_vendors": [
                {
                    "vendor_id": str(uuid4()),
                    "business_name": "Vendor",
                    "subtotal_toman": 6000000,
                    "min_order_value_toman": 5000000,
                    "mov_satisfied": True,
                    "allocated_items_count": 1,
                }
            ],
            "summary": {
                "total_items_requested": 10,
                "total_items_allocated": 10,
                "total_items_unfulfilled": 0,
                "total_amount_toman": 6000000,
                "estimated_delivery_cost_toman": 0,
            },
            "unfulfilled_items": [],
        }


@pytest.fixture
def client():
    app.dependency_overrides[get_application_boundary] = lambda: _FakeBoundary()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_basket_returns_canonical_contract(client):
    response = client.post("/api/v1/baskets")
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "OPEN"
    assert body["data"]["version"] == 1


def test_add_basket_item_returns_new_version(client):
    basket_id = uuid4()
    response = client.post(
        f"/api/v1/baskets/{basket_id}/items",
        json={
            "product_id": str(uuid4()),
            "requested_quantity": 10,
            "pack_quantity": 4,
            "expected_version": 1,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["basket_id"] == str(basket_id)
    assert body["data"]["version"] == 2


def test_add_basket_item_rejects_non_positive_quantity(client):
    response = client.post(
        f"/api/v1/baskets/{uuid4()}/items",
        json={
            "product_id": str(uuid4()),
            "requested_quantity": 0,
            "pack_quantity": 1,
            "expected_version": 1,
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_add_basket_item_rejects_extra_fields(client):
    response = client.post(
        f"/api/v1/baskets/{uuid4()}/items",
        json={
            "product_id": str(uuid4()),
            "requested_quantity": 10,
            "pack_quantity": 1,
            "expected_version": 1,
            "retailer_id": str(uuid4()),
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_allocation_preview_returns_canonical_contract(client):
    response = client.post(f"/api/v1/baskets/{uuid4()}/allocation-preview")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["strategy"] == "MULTI_VENDOR_MIN_FRAGMENTATION"
    assert body["data"]["summary"]["total_amount_toman"] == 6000000


def test_basket_routes_have_no_direct_sql_or_domain_import():
    from pathlib import Path

    route_text = (
        Path(__file__).resolve().parents[0] / "api" / "routes" / "baskets.py"
    ).read_text(encoding="utf-8")

    assert "domain_services" not in route_text
    assert "SELECT " not in route_text
    assert "INSERT " not in route_text
    assert "UPDATE " not in route_text
    assert "DELETE " not in route_text


def test_create_basket_route_is_auth_protected(api_test_environment):
    app.dependency_overrides.clear()
    response = TestClient(app).post("/api/v1/baskets")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


def test_allocation_preview_route_is_auth_protected(api_test_environment):
    app.dependency_overrides.clear()
    response = TestClient(app).post(f"/api/v1/baskets/{uuid4()}/allocation-preview")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"
