"""TODO-133 - CORS, security headers, docs exposure and endpoint configuration.

Checks that the running configuration is the only source of environment-specific
URLs/credentials, that production refuses an unsafe CORS setup, that transport
headers are always present, and that the schema/docs endpoints are not exposed in
production.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scripts.api.main import create_app

REPO_ROOT = Path(__file__).resolve().parents[1]


def _app(monkeypatch, environment: str, origins: str | None = None):
    monkeypatch.setenv("ENVIRONMENT", environment)
    if origins is None:
        monkeypatch.delenv("POL_CORS_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("POL_CORS_ORIGINS", origins)
    return create_app()


def test_production_requires_explicit_cors_origins(monkeypatch):
    with pytest.raises(RuntimeError, match="POL_CORS_ORIGINS"):
        _app(monkeypatch, "production", None)


def test_production_rejects_wildcard_cors(monkeypatch):
    with pytest.raises(RuntimeError, match="Wildcard CORS"):
        _app(monkeypatch, "production", "*,https://app.pol.example")


def test_development_drops_wildcard_and_keeps_allowlist(monkeypatch):
    app = _app(monkeypatch, "development", "*,https://qa.pol.example")
    client = TestClient(app)
    response = client.options(
        "/healthz",
        headers={
            "Origin": "https://qa.pol.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "https://qa.pol.example"

    foreign = client.options(
        "/healthz",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in foreign.headers


def test_default_development_origins_are_loopback_only(monkeypatch):
    app = _app(monkeypatch, "development", None)
    client = TestClient(app)
    local = client.options(
        "/healthz",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert local.headers.get("access-control-allow-origin") == "http://localhost:3000"
    remote = client.options(
        "/healthz",
        headers={"Origin": "https://remote.example", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in remote.headers


def test_security_headers_are_present_in_every_environment(monkeypatch):
    app = _app(monkeypatch, "test", None)
    response = TestClient(app).get("/healthz")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "camera=()" in response.headers["permissions-policy"]
    assert "strict-transport-security" not in response.headers


def test_production_adds_hsts_and_disables_docs(monkeypatch):
    app = _app(monkeypatch, "production", "https://app.pol.example")
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.headers["strict-transport-security"].startswith("max-age=31536000")
    assert client.get("/docs").status_code == 404
    assert client.get("/redoc").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_non_production_exposes_docs(monkeypatch):
    app = _app(monkeypatch, "test", None)
    client = TestClient(app)
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_client_base_urls_come_from_environment_and_default_to_loopback():
    web = io.open(REPO_ROOT / "mvp/apps/web/src/lib/auth/api.ts", encoding="utf-8").read()
    mobile = io.open(REPO_ROOT / "mvp/apps/mobile/src/api.ts", encoding="utf-8").read()

    assert "NEXT_PUBLIC_API_BASE_URL" in web
    assert re.search(r'NEXT_PUBLIC_API_BASE_URL\s*\?\?\s*"http://localhost:8000"', web)

    assert "EXPO_PUBLIC_API_BASE_URL" in mobile
    assert re.search(r'EXPO_PUBLIC_API_BASE_URL\s*\?\?\s*"http://10\.0\.2\.2:8000"', mobile)

    for source in (web, mobile):
        assert "https://api.pol" not in source
        assert "sk_live" not in source


def test_no_hardcoded_credentials_in_shipped_client_sources():
    patterns = {
        "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "github_token": re.compile(r"ghp_[A-Za-z0-9]{36}"),
        "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
        "stripe_live": re.compile(r"sk_live_[A-Za-z0-9]{10,}"),
        "private_key": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
        "db_url_with_password": re.compile(r"postgres(?:ql)?://[^/\s:]+:[^@\s]+@"),
    }
    offenders = []
    for path in list((REPO_ROOT / "mvp/apps").rglob("*.ts")) + list((REPO_ROOT / "mvp/apps").rglob("*.tsx")):
        if "node_modules" in path.parts or "test" in path.parts:
            continue
        text = io.open(path, encoding="utf-8", errors="ignore").read()
        for name, pattern in patterns.items():
            if pattern.search(text):
                offenders.append(f"{name}: {path.relative_to(REPO_ROOT)}")
    assert not offenders, f"credential-shaped literals in client source: {offenders}"
