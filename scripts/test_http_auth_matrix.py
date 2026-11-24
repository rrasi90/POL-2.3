"""HTTP-level auth/session/OTP matrix (TODO-070).

Complements `test_auth_contract.py` (boundary/service level) by exercising the
real FastAPI transport: OTP failure accounting, lockout, rate limiting, session
revocation, refresh replay and cross-user session access.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from scripts.api.main import app
from scripts.test_http_transport import _cleanup, _conn, _seed_user

API = "/api/v1"


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


def _seed():
    return _seed_user()


def _request_otp(client, phone):
    return client.post(f"{API}/auth/request-otp", json={"mobile_number": phone})


def _verify(client, phone, code="123456"):
    return client.post(
        f"{API}/auth/verify-otp",
        json={"mobile_number": phone, "otp_code": code, "client_platform": "web"},
    )


def _attempts(phone):
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT attempts_count, status FROM otp_challenges "
                "WHERE phone_number = %s ORDER BY created_at DESC LIMIT 1",
                (phone,),
            )
            return cur.fetchone()
    finally:
        conn.close()


class TestOtpFailures:
    def test_wrong_otp_persists_attempt_counter(self, client):
        phone, _, _, user_id = _seed()
        try:
            assert _request_otp(client, phone).status_code == 200
            first = _verify(client, phone, "000000")
            assert first.status_code == 422
            assert first.json()["error"]["code"] == "INVALID_REQUEST"
            assert "Attempt 1/5" in first.json()["error"]["message"]
            assert _attempts(phone)[0] == 1

            second = _verify(client, phone, "000000")
            assert second.status_code == 422
            assert "Attempt 2/5" in second.json()["error"]["message"]
            assert _attempts(phone)[0] == 2
        finally:
            _cleanup(phone, user_id)

    def test_fifth_wrong_otp_locks_the_phone(self, client):
        phone, _, _, user_id = _seed()
        try:
            assert _request_otp(client, phone).status_code == 200
            for attempt in range(4):
                resp = _verify(client, phone, "000000")
                assert resp.status_code == 422, resp.text
                assert f"Attempt {attempt + 1}/5" in resp.json()["error"]["message"]
            locked = _verify(client, phone, "000000")
            assert locked.status_code == 429
            assert locked.json()["error"]["code"] == "OTP_LOCKED"
            assert _attempts(phone)[1] == "BLOCKED"
        finally:
            _cleanup(phone, user_id)

    def test_request_otp_during_lockout_is_rejected(self, client):
        phone, _, _, user_id = _seed()
        try:
            assert _request_otp(client, phone).status_code == 200
            for _ in range(5):
                _verify(client, phone, "000000")
            resp = _request_otp(client, phone)
            assert resp.status_code == 429
            assert resp.json()["error"]["code"] == "OTP_LOCKED"
        finally:
            _cleanup(phone, user_id)

    def test_expired_challenge_is_rejected(self, client):
        phone, _, _, user_id = _seed()
        try:
            assert _request_otp(client, phone).status_code == 200
            conn = _conn()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE otp_challenges SET expires_at = %s WHERE phone_number = %s",
                        (datetime.now(timezone.utc) - timedelta(minutes=5), phone),
                    )
                conn.commit()
            finally:
                conn.close()
            resp = _verify(client, phone)
            assert resp.status_code == 422
            assert "expired" in resp.json()["error"]["message"].lower()
        finally:
            _cleanup(phone, user_id)

    def test_consumed_otp_cannot_be_reused(self, client):
        phone, _, _, user_id = _seed()
        try:
            assert _request_otp(client, phone).status_code == 200
            assert _verify(client, phone).status_code == 200
            replay = _verify(client, phone)
            assert replay.status_code == 422
            assert "no pending otp challenge" in replay.json()["error"]["message"].lower()
        finally:
            _cleanup(phone, user_id)

    def test_request_otp_rate_limit_after_three_requests(self, client):
        phone, _, _, user_id = _seed()
        try:
            assert _request_otp(client, phone).status_code == 200
            assert _request_otp(client, phone).status_code == 200
            third = _request_otp(client, phone)
            if third.status_code == 200:
                third = _request_otp(client, phone)
            assert third.status_code == 429
            assert third.json()["error"]["code"] == "OTP_RATE_LIMITED"
        finally:
            _cleanup(phone, user_id)


class TestSessionLifecycle:
    def test_refresh_replay_is_rejected(self, client):
        phone, _, _, user_id = _seed()
        try:
            _request_otp(client, phone)
            login = _verify(client, phone)
            assert login.status_code == 200
            original = login.cookies.get("pol_refresh")

            rotated = client.post(f"{API}/auth/refresh", cookies={"pol_refresh": original})
            assert rotated.status_code == 200
            assert rotated.json()["data"]["access_token"]

            replay = client.post(f"{API}/auth/refresh", cookies={"pol_refresh": original})
            assert replay.status_code == 401
            assert replay.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"
        finally:
            _cleanup(phone, user_id)

    def test_logout_all_revokes_every_session(self, client):
        phone, _, _, user_id = _seed()
        try:
            _request_otp(client, phone)
            login = _verify(client, phone)
            access = login.json()["data"]["access_token"]
            assert client.get(f"{API}/profile", headers={"Authorization": f"Bearer {access}"}).status_code == 200

            logout = client.post(f"{API}/auth/logout-all", headers={"Authorization": f"Bearer {access}"})
            assert logout.status_code == 200
            assert logout.json()["data"]["revoked_sessions"] >= 1
            assert client.get(f"{API}/profile", headers={"Authorization": f"Bearer {access}"}).status_code == 401
        finally:
            _cleanup(phone, user_id)

    def test_cannot_revoke_another_users_session(self, client):
        phone_a, _, _, user_a = _seed()
        phone_b, _, _, user_b = _seed()
        try:
            _request_otp(client, phone_a)
            access_a = _verify(client, phone_a).json()["data"]["access_token"]
            _request_otp(client, phone_b)
            access_b = _verify(client, phone_b).json()["data"]["access_token"]

            conn = _conn()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id FROM user_sessions WHERE user_id = %s "
                        "ORDER BY created_at DESC LIMIT 1",
                        (user_b,),
                    )
                    session_b = cur.fetchone()[0]
            finally:
                conn.close()

            denied = client.delete(
                f"{API}/auth/sessions/{session_b}",
                headers={"Authorization": f"Bearer {access_a}"},
            )
            assert denied.status_code == 403
            assert denied.json()["error"]["code"] == "FORBIDDEN"

            still_valid = client.get(f"{API}/profile", headers={"Authorization": f"Bearer {access_b}"})
            assert still_valid.status_code == 200
        finally:
            _cleanup(phone_a, user_a)
            _cleanup(phone_b, user_b)

    def test_invalid_refresh_cookie_is_unauthorized(self, client):
        resp = client.post(f"{API}/auth/refresh", cookies={"pol_refresh": "not-a-token"})
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"
