"""Request body size guard for the HTTP transport."""

import json

from fastapi.testclient import TestClient

from scripts.api.main import app
from scripts.operational_config import MAX_JSON_BODY_BYTES


def test_oversized_json_body_returns_413_with_canonical_envelope():
    body = json.dumps({"mobile_number": "+989120000000", "pad": "x" * MAX_JSON_BODY_BYTES})
    response = TestClient(app).post(
        "/api/v1/auth/request-otp",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "X-Correlation-ID" in response.headers


def test_multipart_uploads_are_rejected_at_the_api_boundary():
    response = TestClient(app).post(
        "/api/v1/media/presigned-url",
        content=b"--x\r\n\r\n",
        headers={"Content-Type": "multipart/form-data; boundary=x"},
    )
    assert response.status_code == 413
