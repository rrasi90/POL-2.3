"""HTTP error / correlation contract regression tests — Stage 11."""

from __future__ import annotations

import re
import uuid

import pytest
from fastapi.testclient import TestClient

from scripts.api.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("POL_API_DB_NAME", "pol_test")
    monkeypatch.setenv("POL_PG_PORT", os.environ.get("POL_PG_PORT", "5432"))
    monkeypatch.setenv(
        "POL_JWT_SECRET",
        "test-secret-key-for-auth-contract-tests-only-32bytes!!",
    )
    monkeypatch.setenv("ENVIRONMENT", "test")
    return TestClient(app)


import os  # noqa: E402  (kept after fixture for readability; used inside fixture)


UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _assert_error_envelope(body: dict, code: str):
    assert body["success"] is False
    error = body["error"]
    assert error["code"] == code
    assert isinstance(error["message"], str) and error["message"]
    assert "details" in error
    assert "timestamp" in error
    assert error["timestamp"].endswith("Z")


def test_unknown_route_returns_canonical_404_envelope(client):
    response = client.get("/api/v1/definitely-not-a-route")
    assert response.status_code == 404
    _assert_error_envelope(response.json(), "NOT_FOUND")


def test_method_not_allowed_returns_405_envelope(client):
    response = client.delete("/api/v1/auth/refresh")
    assert response.status_code == 405
    _assert_error_envelope(response.json(), "METHOD_NOT_ALLOWED")


def test_validation_error_returns_422_with_field_details(client):
    response = client.post("/api/v1/auth/request-otp", json={"unexpected_field": "x"})
    assert response.status_code == 422
    body = response.json()
    _assert_error_envelope(body, "VALIDATION_ERROR")
    fields = body["error"]["details"]["fields"]
    assert isinstance(fields, list) and fields
    assert all("loc" in f and "type" in f and "message" in f for f in fields)


def test_missing_bearer_token_returns_401_envelope(client):
    response = client.get("/api/v1/profile")
    assert response.status_code == 401
    _assert_error_envelope(response.json(), "INVALID_ACCESS_TOKEN")


def test_correlation_id_valid_supplied_is_echoed(client):
    supplied = f"corr-{uuid.uuid4()}"
    response = client.get(
        "/api/v1/definitely-not-a-route", headers={"X-Correlation-ID": supplied}
    )
    assert response.headers.get("X-Correlation-ID") == supplied


def test_correlation_id_invalid_supplied_is_replaced_with_uuid(client):
    response = client.get(
        "/api/v1/definitely-not-a-route", headers={"X-Correlation-ID": "bad id with spaces!"}
    )
    correlation_id = response.headers.get("X-Correlation-ID")
    assert correlation_id
    assert UUID_RE.fullmatch(correlation_id)


def test_correlation_id_missing_is_generated(client):
    response = client.get("/api/v1/definitely-not-a-route")
    correlation_id = response.headers.get("X-Correlation-ID")
    assert correlation_id
    assert UUID_RE.fullmatch(correlation_id)


def test_correlation_id_present_on_error_responses(client):
    response = client.post("/api/v1/auth/request-otp", json={"unexpected_field": "x"})
    assert response.status_code == 422
    correlation_id = response.headers.get("X-Correlation-ID")
    assert correlation_id
    assert UUID_RE.fullmatch(correlation_id)
