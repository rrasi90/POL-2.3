import pytest

from scripts.api import db as db_module


def test_production_db_requires_password_and_tls(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("POL_API_DB_HOST", "db.example")
    monkeypatch.setenv("POL_API_DB_NAME", "pol")
    monkeypatch.setenv("POL_API_DB_USER", "pol_app")
    monkeypatch.delenv("POL_API_DB_PASSWORD", raising=False)
    monkeypatch.delenv("PGPASSWORD", raising=False)
    monkeypatch.setenv("POL_API_DB_SSLMODE", "require")

    with pytest.raises(RuntimeError, match="requires POL_API_DB_PASSWORD"):
        db_module.get_runtime_connection()

    monkeypatch.setenv("POL_API_DB_PASSWORD", "secret")
    monkeypatch.setenv("POL_API_DB_SSLMODE", "prefer")
    with pytest.raises(RuntimeError, match="requires encrypted transport"):
        db_module.get_runtime_connection()


def test_production_db_passes_explicit_secure_config(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("POL_API_DB_HOST", "db.example")
    monkeypatch.setenv("POL_API_DB_NAME", "pol")
    monkeypatch.setenv("POL_API_DB_USER", "pol_app")
    monkeypatch.setenv("POL_API_DB_PASSWORD", "secret")
    monkeypatch.setenv("POL_API_DB_SSLMODE", "verify-full")

    captured = {}

    def fake_connect(**kwargs):
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(db_module.psycopg2, "connect", fake_connect)
    result = db_module.get_runtime_connection()

    assert result is not None
    assert captured["dbname"] == "pol"
    assert captured["host"] == "db.example"
    assert captured["user"] == "pol_app"
    assert captured["password"] == "secret"
    assert captured["sslmode"] == "verify-full"
