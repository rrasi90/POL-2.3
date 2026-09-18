"""HTTP transport tests for vendor order lifecycle transitions."""

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
    def vendor_order_accept(self, *, order_id):
        return {
            "order_id": order_id,
            "order_number": "ORD-HTTP-ACCEPT",
            "order_group_id": str(uuid4()),
            "order_status": "ACCEPTED",
            "total_amount_toman": 5000000,
            "accepted_item_count": 1,
            "reservation_count": 1,
        }

    def vendor_order_reject(self, *, order_id, rejection_reason):
        return {
            "order_id": order_id,
            "order_number": "ORD-HTTP-REJECT",
            "order_group_id": str(uuid4()),
            "order_status": "REJECTED",
            "total_amount_toman": 5000000,
            "rejection_reason": rejection_reason,
            "released_reservation_count": 1,
        }


@pytest.fixture
def client():
    app.dependency_overrides[get_application_boundary] = lambda: _FakeBoundary()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_vendor_accept_route_returns_canonical_contract(client):
    order_id = uuid4()
    response = client.post(f"/api/v1/orders/{order_id}/accept")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["order_id"] == str(order_id)
    assert body["data"]["order_status"] == "ACCEPTED"


def test_vendor_accept_route_rejects_invalid_order_id(client):
    response = client.post("/api/v1/orders/not-a-uuid/accept")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_vendor_accept_route_has_no_request_body_contract(client):
    order_id = uuid4()
    response = client.post(
        f"/api/v1/orders/{order_id}/accept",
        json={"vendor_id": str(uuid4())},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_vendor_accept_route_is_auth_protected(api_test_environment):
    app.dependency_overrides.clear()
    response = TestClient(app).post(f"/api/v1/orders/{uuid4()}/accept")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"


def test_vendor_accept_route_source_boundary_has_no_domain_import_or_sql():
    from pathlib import Path

    route_text = (
        Path(__file__).resolve().parents[0] / "api" / "routes" / "orders.py"
    ).read_text(encoding="utf-8")

    assert "domain_services" not in route_text
    assert "SELECT " not in route_text
    assert "INSERT " not in route_text
    assert "UPDATE " not in route_text
    assert "DELETE " not in route_text


def test_vendor_reject_route_returns_canonical_contract(client):
    order_id = uuid4()
    response = client.post(
        f"/api/v1/orders/{order_id}/reject",
        json={"reason": "Out of physical stock"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["order_id"] == str(order_id)
    assert body["data"]["order_status"] == "REJECTED"
    assert body["data"]["rejection_reason"] == "Out of physical stock"


def test_vendor_reject_route_requires_reason(client):
    response = client.post(f"/api/v1/orders/{uuid4()}/reject")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_vendor_reject_route_forbids_unknown_body_fields(client):
    response = client.post(
        f"/api/v1/orders/{uuid4()}/reject",
        json={"reason": "Out of physical stock", "vendor_id": str(uuid4())},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_vendor_reject_route_rejects_invalid_order_id(client):
    response = client.post(
        "/api/v1/orders/not-a-uuid/reject",
        json={"reason": "Out of physical stock"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
