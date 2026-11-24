"""Correlation IDs, access logs and security headers over HTTP (TODO-086)."""

from __future__ import annotations

import logging
import uuid

import pytest
from fastapi.testclient import TestClient

from scripts.api.main import app
from scripts.api.logging_config import LOGGER_NAME

SECRET_PHONE = "+989121234567"


@pytest.fixture()
def client():
    return TestClient(app)


def _records(caplog):
    return [r for r in caplog.records if r.name == LOGGER_NAME]


class TestCorrelationHeader:
    def test_valid_correlation_id_is_echoed(self, client):
        supplied = "test-correlation-123"
        response = client.get("/healthz", headers={"X-Correlation-ID": supplied})
        assert response.status_code == 200
        assert response.headers["X-Correlation-ID"] == supplied

    def test_missing_correlation_id_is_generated(self, client):
        response = client.get("/healthz")
        generated = response.headers["X-Correlation-ID"]
        uuid.UUID(generated)

    @pytest.mark.parametrize(
        "supplied",
        ["bad id with spaces", "x" * 129, "line\nbreak", "semi;colon", ""],
    )
    def test_invalid_correlation_id_is_replaced(self, client, supplied):
        response = client.get("/healthz", headers={"X-Correlation-ID": supplied})
        value = response.headers["X-Correlation-ID"]
        assert value != supplied
        uuid.UUID(value)

    def test_correlation_id_survives_error_responses(self, client):
        supplied = "error-path-correlation"
        response = client.get(
            "/api/v1/baskets/current",
            headers={"X-Correlation-ID": supplied},
        )
        assert response.status_code == 401
        assert response.headers["X-Correlation-ID"] == supplied


class TestSecurityHeaders:
    def test_baseline_headers_are_present(self, client):
        response = client.get("/healthz")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert "camera=()" in response.headers["Permissions-Policy"]

    def test_headers_are_present_on_errors_too(self, client):
        response = client.get("/api/v1/baskets/current")
        assert response.status_code == 401
        assert response.headers["X-Content-Type-Options"] == "nosniff"


class TestAccessLogging:
    def test_successful_request_is_logged_with_correlation(self, client, caplog):
        caplog.set_level(logging.INFO, logger=LOGGER_NAME)
        supplied = "log-success-correlation"
        client.get("/healthz", headers={"X-Correlation-ID": supplied})
        records = [r for r in _records(caplog) if r.getMessage() == "request.completed"]
        assert records, "no access log record was emitted"
        fields = records[-1].fields
        assert fields["correlation_id"] == supplied
        assert fields["method"] == "GET"
        assert fields["path"] == "/healthz"
        assert fields["status"] == 200
        assert fields["duration_ms"] >= 0

    def test_error_request_is_logged_with_status(self, client, caplog):
        caplog.set_level(logging.INFO, logger=LOGGER_NAME)
        supplied = "log-error-correlation"
        client.get(
            "/api/v1/baskets/current",
            headers={"X-Correlation-ID": supplied, "Authorization": "Bearer garbage"},
        )
        records = [r for r in _records(caplog) if r.getMessage() == "request.completed"]
        assert records
        fields = records[-1].fields
        assert fields["correlation_id"] == supplied
        assert fields["status"] == 401
        assert fields["path"] == "/api/v1/baskets/current"

    def test_logs_never_contain_secrets_or_pii(self, client, caplog):
        caplog.set_level(logging.INFO, logger=LOGGER_NAME)
        client.post(
            "/api/v1/auth/request-otp",
            json={"mobile_number": SECRET_PHONE, "client_fingerprint": "device-abc"},
        )
        client.post(
            "/api/v1/auth/verify-otp",
            json={"mobile_number": SECRET_PHONE, "otp_code": "123456"},
        )
        client.get(
            "/api/v1/baskets/current",
            headers={"Authorization": "Bearer super-secret-token-value"},
        )
        rendered = "\n".join(record.getMessage() for record in caplog.records)
        assert SECRET_PHONE not in rendered
        assert "989121234567" not in rendered
        assert "123456" not in rendered
        assert "super-secret-token-value" not in rendered
        assert "Bearer " not in rendered
        assert "device-abc" not in rendered

    def test_registered_routes_do_not_log_bodies(self, client, caplog):
        caplog.set_level(logging.INFO, logger=LOGGER_NAME)
        client.post("/api/v1/auth/request-otp", json={"mobile_number": SECRET_PHONE})
        for record in caplog.records:
            assert "mobile_number" not in record.getMessage()
            assert "json" not in record.getMessage().lower()


class TestCorrelationPropagationSourceContract:
    def test_request_correlation_reaches_application_context(self):
        import inspect

        from scripts.api import dependencies

        source = inspect.getsource(dependencies.get_application_context)
        assert "request.state.correlation_id" in source
        assert "correlation_id=" in source

    def test_failure_path_is_logged_before_reraising(self):
        import inspect

        import scripts.api.main as main_module

        source = inspect.getsource(main_module.create_app)
        assert "request.failed" in source
        assert "access_log.error" in source


class TestCorrelationReachesDatabase:
    def test_x_correlation_id_is_persisted_in_the_audit_log(self):
        from scripts.test_http_admin_referrals import _db, _seed_admin_vendor_retailer

        data = _seed_admin_vendor_retailer()
        header = 'trace-' + uuid.uuid4().hex[:12]
        client = TestClient(app)
        response = client.post(
            '/api/v1/admin/categories',
            json={'name_fa': 'دسته تست همبستگی', 'slug': 'corr-' + uuid.uuid4().hex[:8]},
            headers={
                'Authorization': 'Bearer ' + data['a_token'],
                'X-Correlation-ID': header,
            },
        )
        assert response.status_code == 201, response.text
        conn = _db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT count(*) FROM admin_audit_logs WHERE correlation_id = %s',
                    (header,),
                )
                assert cur.fetchone()[0] >= 1
        finally:
            conn.close()
