"""
POL Auth Contract Verification Suite — Batch 6B-2.1 (pytest-native)
Tests the D-018 auth runtime contract with proper validation:
- JWT claims, access token lifetime, refresh session lifetime
- OTP PBKDF2 hashing, timing-safe comparison
- Rate limit (3/5min/phone+IP) with advisory lock serialization
- Phone lockout (10min after 5th failed attempt)
- Organization switch: old JWT rejected via validate_access_token
- Session revocation: validate_access_token rejects revoked sessions
- Refresh token flow with hash persistence verification
- Purpose policy: D-018 applies to LOGIN/REGISTER only
- Concurrency test for rate-limit serialization

Stage 08 refactor note: the former standalone runner held every test inside
run_tests() closures, which pytest could not collect — the suite was a CI
blind spot (0 collected tests). Every test body, assertion, execution order,
shared dataset and cleanup is preserved verbatim; only the runner layer
changed. A module-scoped fixture provides the shared user/connection and an
autouse fixture mirrors the former safe_test(conn.rollback()) failure
isolation after every test.
"""

import os
import sys
import threading
import uuid
from datetime import datetime, timedelta, timezone

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.auth_boundary import (
    AuthError,
    encode_access_token,
    decode_access_token,
    validate_access_token,
    generate_refresh_token,
    hash_token,
    store_otp_hash,
    verify_otp_hash,
)
from scripts.operational_config import (
    OTP_MAX_ATTEMPTS,
    OTP_RATE_LIMIT_COUNT,
    OTP_RATE_LIMIT_WINDOW_MINUTES,
    OTP_LOCKOUT_MINUTES,
    SESSION_TTL_HOURS,
    JWT_ACCESS_TTL_SECONDS,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def get_connection():
    ports = [int(os.environ.get("POL_PG_PORT", 5432)), 5432, 5433]
    tried = []
    for p in ports:
        if p in tried:
            continue
        tried.append(p)
        try:
            conn = psycopg2.connect(dbname="pol_test", user="postgres", host="127.0.0.1", port=p)
            conn.autocommit = False
            return conn
        except Exception:
            continue
    raise ConnectionError(f"Could not connect to PostgreSQL on ports {tried}")


def setup_test_user(cur):
    """Create a test user and two orgs with memberships."""
    user_id = str(uuid.uuid4())
    org_a = str(uuid.uuid4())
    org_b = str(uuid.uuid4())

    phone_suffix = uuid.uuid4().hex[:8]
    cur.execute("""
        INSERT INTO users (id, phone_number, role, full_name, is_active)
        VALUES (%s, %s, 'RETAILER_OWNER', 'Auth Test User', TRUE);
    """, (user_id, f"+98916{phone_suffix}"))

    for idx, (org_id, org_type, role) in enumerate([(org_a, "RETAILER", "RETAILER_OWNER"), (org_b, "VENDOR", "VENDOR_OWNER")]):
        cur.execute("""
            INSERT INTO organizations (id, name, org_type, status)
            VALUES (%s, %s, %s, 'ACTIVE');
        """, (org_id, f"Org {org_id[:8]}", org_type))
        cur.execute("""
            INSERT INTO organization_memberships (id, organization_id, user_id, role, status, is_primary)
            VALUES (%s, %s, %s, %s, 'ACTIVE', %s);
        """, (str(uuid.uuid4()), org_id, user_id, role, idx == 0))

    return user_id, org_a, org_b


def cleanup(cur, user_id, org_a, org_b):
    """Clean up test data."""
    try:
        conn = cur.connection
        conn.rollback()  # Clear any failed transaction state
        cur.execute("DELETE FROM user_sessions WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM otp_challenges WHERE phone_number LIKE '+9891611100%';")
        cur.execute("DELETE FROM otp_challenges WHERE phone_number LIKE '+98916concurrent%';")
        cur.execute("DELETE FROM organization_memberships WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM organizations WHERE id IN (%s, %s);", (org_a, org_b))
        cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
    except Exception:
        try:
            cur.connection.rollback()
        except Exception:
            pass


@pytest.fixture(scope="module")
def auth_env():
    """Shared auth test environment: one user, two orgs, one connection.

    Mirrors the former standalone runner setup exactly (single user reused
    by every test; final cleanup at module teardown).
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    user_id, org_a, org_b = setup_test_user(cur)
    conn.commit()

    os.environ.setdefault("POL_JWT_SECRET", "test-secret-key-for-auth-contract-tests-only-32bytes!!")

    yield {"conn": conn, "cur": cur, "user_id": user_id, "org_a": org_a, "org_b": org_b}

    cleanup(cur, user_id, org_a, org_b)
    cur.close()
    conn.close()


@pytest.fixture(autouse=True)
def _auth_tx_recovery(auth_env):
    """Mirror the former safe_test failure isolation: roll back any pending
    or aborted transaction state after every test so one failure cannot
    poison the shared connection for the rest of the module."""
    yield
    try:
        auth_env["conn"].rollback()
    except Exception:
        pass


# =========================================================
# T-SEC-OTP-01: Deterministic OTP is test-environment only
# =========================================================
def test_static_otp_is_strictly_test_only(auth_env, monkeypatch):
    """Prevent a non-test deployment from silently falling back to 1234."""
    from scripts import domain_services
    from scripts.domain_services import AuthService

    cur = auth_env["cur"]
    phone = f"+9891{uuid.uuid4().hex[:8]}"
    ip = "10.240.0.10"

    # Explicit test environment may expose the deterministic fixture code.
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.delenv("POL_ENV", raising=False)
    first = AuthService.request_otp(cur, phone, ip, "LOGIN")
    assert first["test_code"] == "1234"
    cur.execute(
        "SELECT code_hash FROM otp_challenges WHERE id=%s",
        (first["id"],),
    )
    assert verify_otp_hash("1234", cur.fetchone()["code_hash"])

    # Development/unknown/unset environments must never use or expose 1234.
    monkeypatch.setattr(domain_services.secrets, "randbelow", lambda upper: 5678)
    for env in ("development", "unknown", ""):
        if env:
            monkeypatch.setenv("ENVIRONMENT", env)
        else:
            monkeypatch.delenv("ENVIRONMENT", raising=False)
        result = AuthService.request_otp(cur, phone, ip, "LOGIN")
        assert "test_code" not in result
        cur.execute(
            "SELECT code_hash FROM otp_challenges WHERE id=%s",
            (result["id"],),
        )
        stored_hash = cur.fetchone()["code_hash"]
        assert verify_otp_hash("5678", stored_hash)
        assert not verify_otp_hash("1234", stored_hash)

    cur.execute("DELETE FROM otp_challenges WHERE phone_number=%s", (phone,))
    auth_env["conn"].commit()


# =========================================================
# T-AC1: JWT claims complete
# =========================================================
def test_ac1_jwt_claims_complete(auth_env):
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    token = encode_access_token(user_id, str(uuid.uuid4()), org_a, "RETAILER_OWNER")
    claims = decode_access_token(token)
    assert claims["sub"] == user_id
    assert "sid" in claims
    assert claims["org_id"] == org_a
    assert claims["role"] == "RETAILER_OWNER"
    assert claims["iss"] == "pol-platform"
    assert claims["aud"] == "pol-api"
    assert "iat" in claims and "exp" in claims


# =========================================================
# T-AC2: JWT exp = iat + 15 min
# =========================================================
def test_ac2_jwt_exp_equals_iat_plus_15_min(auth_env):
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    token = encode_access_token(user_id, str(uuid.uuid4()), org_a, "RETAILER_OWNER")
    claims = decode_access_token(token)
    assert claims["exp"] - claims["iat"] == 900


# =========================================================
# T-AC3: SESSION_TTL_HOURS = 720 (30 days)
# =========================================================
def test_ac3_session_ttl_is_720_hours():
    assert SESSION_TTL_HOURS == 720


# =========================================================
# T-AC11: OTP PBKDF2 hash + timing-safe verify
# =========================================================
def test_ac11_otp_pbkdf2_hash_and_timing_safe_verify():
    stored = store_otp_hash("1234")
    parts = stored.split("$")
    assert len(parts) == 3
    assert int(parts[0]) == 100_000
    assert verify_otp_hash("1234", stored) is True
    assert verify_otp_hash("9999", stored) is False


# =========================================================
# T-AC12: SESSION_TTL_HOURS = 720
# =========================================================
def test_ac12_session_ttl_is_720_hours():
    assert SESSION_TTL_HOURS == 720


# =========================================================
# T-AC13: validate_access_token — valid token accepted
# =========================================================
def test_ac13_validate_access_token_valid_token_accepted(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id = str(uuid.uuid4())
    token = encode_access_token(user_id, sess_id, org_a, "RETAILER_OWNER")
    cur.execute("""
        INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days');
    """, (sess_id, user_id, org_a, hash_token(token)))
    conn.commit()
    result = validate_access_token(cur, token)
    assert result["sub"] == user_id
    assert result["org_id"] == org_a
    cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
    conn.commit()


# =========================================================
# T-AC14: validate_access_token — expired token rejected
# =========================================================
def test_ac14_validate_access_token_expired_token_rejected(auth_env):
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    claims = {
        "sub": user_id, "sid": sess_id, "org_id": org_a, "role": "RETAILER_OWNER",
        "iss": "pol-platform", "aud": "pol-api",
        "iat": now - timedelta(seconds=2000),
        "exp": now - timedelta(seconds=100),
    }
    import jwt as _jwt
    token = _jwt.encode(claims, os.environ["POL_JWT_SECRET"], algorithm="HS256")
    try:
        validate_access_token(cur, token)
        raise AssertionError("No exception raised")
    except AuthError as e:
        assert "expired" in str(e).lower()


# =========================================================
# T-AC15: validate_access_token — session not found → rejected
# =========================================================
def test_ac15_validate_access_token_no_session_rejected(auth_env):
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    fake_session_id = str(uuid.uuid4())
    token = encode_access_token(user_id, fake_session_id, org_a, "RETAILER_OWNER")
    try:
        validate_access_token(cur, token)
        raise AssertionError("No exception raised")
    except AuthError as e:
        assert "session" in str(e).lower()


# =========================================================
# T-AC16: validate_access_token — REVOKED session → rejected
# =========================================================
def test_ac16_validate_access_token_revoked_session_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id = str(uuid.uuid4())
    token = encode_access_token(user_id, sess_id, org_a, "RETAILER_OWNER")
    cur.execute("""
        INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days');
    """, (sess_id, user_id, org_a, hash_token(token)))
    conn.commit()
    cur.execute("UPDATE user_sessions SET status = 'REVOKED' WHERE id = %s;", (sess_id,))
    conn.commit()
    try:
        validate_access_token(cur, token)
        raise AssertionError("No exception raised")
    except AuthError as e:
        assert "not active" in str(e).lower() or "session" in str(e).lower()
    finally:
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


# =========================================================
# T-AC17: validate_access_token — stale org_id → rejected
# =========================================================
def test_ac17_validate_access_token_stale_org_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    org_b = auth_env["org_b"]
    sess_id = str(uuid.uuid4())
    token_a = encode_access_token(user_id, sess_id, org_a, "RETAILER_OWNER")
    cur.execute("""
        INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days');
    """, (sess_id, user_id, org_a, hash_token(token_a)))
    conn.commit()
    cur.execute("""
        UPDATE user_sessions SET active_organization_id = %s WHERE id = %s;
    """, (org_b, sess_id))
    conn.commit()
    try:
        validate_access_token(cur, token_a)
        raise AssertionError("No exception raised")
    except AuthError as e:
        assert "organization" in str(e).lower()
    finally:
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


# =========================================================
# T-AC18: validate_access_token — new org B JWT → accepted
# =========================================================
def test_ac18_validate_access_token_new_org_accepted(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    org_b = auth_env["org_b"]
    sess_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days');
    """, (sess_id, user_id, org_a, "placeholder"))
    conn.commit()
    cur.execute("""
        UPDATE user_sessions SET active_organization_id = %s WHERE id = %s;
    """, (org_b, sess_id))
    conn.commit()
    token_b = encode_access_token(user_id, sess_id, org_b, "VENDOR_OWNER")
    cur.execute("""
        UPDATE user_sessions SET token_hash = %s WHERE id = %s;
    """, (hash_token(token_b), sess_id))
    conn.commit()
    result = validate_access_token(cur, token_b)
    assert result["org_id"] == org_b
    assert result["role"] == "VENDOR_OWNER"
    cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
    conn.commit()


# =========================================================
# T-AC19: validate_access_token — membership revoked → rejected
# =========================================================
def test_ac19_validate_access_token_membership_revoked_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id = str(uuid.uuid4())
    token = encode_access_token(user_id, sess_id, org_a, "RETAILER_OWNER")
    cur.execute("""
        INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days');
    """, (sess_id, user_id, org_a, hash_token(token)))
    conn.commit()
    cur.execute("""
        UPDATE organization_memberships SET status = 'REVOKED'
        WHERE user_id = %s AND organization_id = %s;
    """, (user_id, org_a))
    conn.commit()
    try:
        validate_access_token(cur, token)
        raise AssertionError("No exception raised")
    except AuthError as e:
        assert "membership" in str(e).lower()
    finally:
        cur.execute("""
            UPDATE organization_memberships SET status = 'ACTIVE'
            WHERE user_id = %s AND organization_id = %s;
        """, (user_id, org_a))
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


# =========================================================
# T-AC20: OTP challenge is consumed exactly once under verification
# =========================================================
def test_ac20_otp_challenge_is_consumed_exactly_once(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    phone = "+989161110030"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
        VALUES (%s, %s, %s, 'LOGIN', '10.0.0.30', 0, 5, 'PENDING', now() + interval '2 minutes');
    """, (otp_id, phone, store_otp_hash("1234")))
    conn.commit()
    from scripts.domain_services import AuthService
    first = AuthService.verify_otp(cur, phone, "1234", user_id, org_a)
    assert first["access_token"]
    cur.execute("SELECT status FROM otp_challenges WHERE id = %s;", (otp_id,))
    assert cur.fetchone()["status"] == "VERIFIED"
    try:
        AuthService.verify_otp(cur, phone, "1234", user_id, org_a)
        raise AssertionError("OTP was accepted more than once")
    except ValueError as e:
        assert "No pending OTP challenge" in str(e)
    finally:
        cur.execute("DELETE FROM user_sessions WHERE user_id = %s;", (user_id,))
        cur.execute("DELETE FROM otp_challenges WHERE id = %s;", (otp_id,))
        conn.commit()


# =========================================================
# T-AC4: Refresh token hash actually persisted
# =========================================================
def test_ac4_refresh_token_hash_actually_persisted(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id = str(uuid.uuid4())
    token = encode_access_token(user_id, sess_id, org_a, "RETAILER_OWNER")
    refresh_token = generate_refresh_token()
    refresh_hash = hash_token(refresh_token)
    cur.execute("""
        INSERT INTO user_sessions (id, user_id, active_organization_id, token_hash, refresh_token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, %s, 'ACTIVE', now() + interval '30 days');
    """, (sess_id, user_id, org_a, hash_token(token), refresh_hash))
    conn.commit()
    cur.execute("SELECT refresh_token_hash FROM user_sessions WHERE id = %s;", (sess_id,))
    stored_hash = cur.fetchone()["refresh_token_hash"]
    assert stored_hash == hash_token(refresh_token), "Refresh token hash mismatch"
    cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
    conn.commit()


# =========================================================
# RATE LIMIT TESTS
# =========================================================

def test_rl1_4th_request_same_phone_ip_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110001"
    ip = "192.168.1.100"
    for i in range(OTP_RATE_LIMIT_COUNT):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    try:
        AuthService.request_otp(cur, phone, ip, "LOGIN")
        raise AssertionError("No exception")
    except PermissionError as e:
        assert "Rate limit" in str(e)
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        conn.commit()


def test_rl2_same_phone_different_ips_separate_buckets(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110002"
    for i in range(OTP_RATE_LIMIT_COUNT):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone, "10.0.0.1"))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone, "10.0.0.2", "LOGIN")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


def test_rl3_same_phone_ip_after_5min_allowed(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110003"
    ip = "192.168.1.200"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
        VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() - interval '6 minutes');
    """, (otp_id, phone, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone, ip, "LOGIN")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


def test_rl6_different_phone_unaffected_by_rate_limit(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone_a = "+989161110006"
    phone_b = "+989161110007"
    ip = "192.168.1.500"
    for i in range(3):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone_a, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone_b, ip, "LOGIN")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number IN (%s, %s);", (phone_a, phone_b))
    conn.commit()


def test_rl7_order_confirmation_bypasses_d018_rate_limit(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110020"
    ip = "192.168.1.700"
    for i in range(OTP_RATE_LIMIT_COUNT):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone, ip, "ORDER_CONFIRMATION")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


def test_rl8_delivery_confirm_bypasses_d018_rate_limit(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110021"
    ip = "192.168.1.701"
    for i in range(OTP_RATE_LIMIT_COUNT):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone, ip, "DELIVERY_CONFIRM")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


def test_rl9_login_is_d018_enforced(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110022"
    ip = "192.168.1.702"
    for i in range(OTP_RATE_LIMIT_COUNT):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'LOGIN', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    try:
        AuthService.request_otp(cur, phone, ip, "LOGIN")
        raise AssertionError("No exception")
    except PermissionError:
        pass
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        conn.commit()


def test_rl10_register_is_d018_enforced(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110023"
    ip = "192.168.1.703"
    for i in range(OTP_RATE_LIMIT_COUNT):
        otp_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
            VALUES (%s, %s, 'hash', 'REGISTER', %s, 0, 5, 'PENDING', now() + interval '2 minutes');
        """, (otp_id, phone, ip))
    conn.commit()
    from scripts.domain_services import AuthService
    try:
        AuthService.request_otp(cur, phone, ip, "REGISTER")
        raise AssertionError("No exception")
    except PermissionError:
        pass
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        conn.commit()


# =========================================================
# LOCKOUT TESTS
# =========================================================

def test_lo1_5th_wrong_otp_blocked_with_blocked_at(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110010"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
        VALUES (%s, %s, %s, 'LOGIN', '10.0.0.1', 0, 5, 'PENDING', now() + interval '2 minutes');
    """, (otp_id, phone, store_otp_hash("5678")))
    conn.commit()
    for attempt in range(1, 6):
        cur.execute("""
            UPDATE otp_challenges
            SET attempts_count = attempts_count + 1,
                status = CASE WHEN attempts_count + 1 >= max_attempts THEN 'BLOCKED' ELSE 'PENDING' END,
                blocked_at = CASE WHEN attempts_count + 1 >= max_attempts THEN now() ELSE blocked_at END
            WHERE id = %s
            RETURNING attempts_count, status, blocked_at;
        """, (otp_id,))
        res = cur.fetchone()
    conn.commit()
    assert res["status"] == "BLOCKED"
    assert res["blocked_at"] is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


def test_lo2_request_during_lockout_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110011"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, blocked_at, expires_at)
        VALUES (%s, %s, 'hash', 'LOGIN', '10.0.0.1', 5, 5, 'BLOCKED', now(), now() + interval '2 minutes');
    """, (otp_id, phone,))
    conn.commit()
    from scripts.domain_services import AuthService
    try:
        AuthService.request_otp(cur, phone, "10.0.0.2", "LOGIN")
        raise AssertionError("No exception")
    except PermissionError as e:
        assert "locked" in str(e).lower()
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        conn.commit()


def test_lo3_blocked_at_10min_plus_1s_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110012"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, blocked_at, expires_at)
        VALUES (%s, %s, 'hash', 'LOGIN', '10.0.0.1', 5, 5, 'BLOCKED', now() - interval '10 minutes' + interval '1 second', now() + interval '2 minutes');
    """, (otp_id, phone,))
    conn.commit()
    from scripts.domain_services import AuthService
    try:
        AuthService.request_otp(cur, phone, "10.0.0.2", "LOGIN")
        raise AssertionError("No exception")
    except PermissionError:
        pass
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        conn.commit()


def test_lo4_blocked_at_10min_minus_1s_allowed(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110013"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, blocked_at, expires_at)
        VALUES (%s, %s, 'hash', 'LOGIN', '10.0.0.1', 5, 5, 'BLOCKED', now() - interval '10 minutes' - interval '1 second', now() + interval '2 minutes');
    """, (otp_id, phone,))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone, "10.0.0.2", "LOGIN")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


def test_lo5_phone_locked_different_ip_rejected(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110014"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, blocked_at, expires_at)
        VALUES (%s, %s, 'hash', 'LOGIN', '10.0.0.1', 5, 5, 'BLOCKED', now(), now() + interval '2 minutes');
    """, (otp_id, phone,))
    conn.commit()
    from scripts.domain_services import AuthService
    try:
        AuthService.request_otp(cur, phone, "10.0.0.99", "LOGIN")
        raise AssertionError("No exception")
    except PermissionError:
        pass
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
        conn.commit()


def test_lo6_phone_a_locked_phone_b_allowed(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone_a = "+989161110015"
    phone_b = "+989161110016"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, blocked_at, expires_at)
        VALUES (%s, %s, 'hash', 'LOGIN', '10.0.0.1', 5, 5, 'BLOCKED', now(), now() + interval '2 minutes');
    """, (otp_id, phone_a,))
    conn.commit()
    from scripts.domain_services import AuthService
    result = AuthService.request_otp(cur, phone_b, "10.0.0.1", "LOGIN")
    assert result is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number IN (%s, %s);", (phone_a, phone_b))
    conn.commit()


def test_lo7_lockout_starts_at_5th_attempt_not_creation(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+989161110017"
    otp_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO otp_challenges (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
        VALUES (%s, %s, %s, 'LOGIN', '10.0.0.1', 0, 5, 'PENDING', now() + interval '2 minutes');
    """, (otp_id, phone, store_otp_hash("5678")))
    conn.commit()
    cur.execute("""
        UPDATE otp_challenges
        SET attempts_count = 5, status = 'BLOCKED', blocked_at = now()
        WHERE id = %s RETURNING blocked_at;
    """, (otp_id,))
    blocked_at = cur.fetchone()["blocked_at"]
    conn.commit()
    assert blocked_at is not None
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


# =========================================================
# CONCURRENCY TEST (T-CON1)
# =========================================================
def test_con1_concurrent_rate_limit_advisory_lock(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    phone = "+98916concurrent01"
    ip = "10.99.0.1"
    results = {"count": 0, "errors": []}

    def insert_otp():
        try:
            c = get_connection()
            c.autocommit = False
            cur2 = c.cursor(cursor_factory=RealDictCursor)
            from scripts.domain_services import AuthService
            AuthService.request_otp(cur2, phone, ip, "LOGIN")
            c.commit()
            results["count"] += 1
        except PermissionError:
            pass
        except Exception as e:
            results["errors"].append(str(e))
        finally:
            try:
                c.close()
            except Exception:
                pass

    threads = [threading.Thread(target=insert_otp) for _ in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)

    assert results["count"] <= OTP_RATE_LIMIT_COUNT, \
        f"Expected at most {OTP_RATE_LIMIT_COUNT} OTPs, got {results['count']}"
    assert results["count"] >= 1, f"At least 1 OTP should succeed, got {results['count']}. Errors: {results['errors']}"
    assert len(results["errors"]) == 0, f"Unexpected errors: {results['errors']}"
    cur.execute("DELETE FROM otp_challenges WHERE phone_number = %s;", (phone,))
    conn.commit()


if __name__ == "__main__":
    raise SystemExit(pytest.main([os.path.abspath(__file__)]))



# =========================================================
# P0 REGRESSION: SESSION OWNERSHIP / REFRESH ROTATION / OTP BINDING
# =========================================================
def test_p0_switch_organization_rejects_foreign_session(auth_env):
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    org_b = auth_env["org_b"]

    foreign_user = str(uuid.uuid4())
    foreign_phone = f"+9891{uuid.uuid4().hex[:8]}"
    cur.execute(
        "INSERT INTO users (id, phone_number, role, full_name, is_active) "
        "VALUES (%s, %s, 'RETAILER_OWNER', 'Foreign Session User', TRUE)",
        (foreign_user, foreign_phone),
    )
    foreign_session = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO user_sessions "
        "(id, user_id, active_organization_id, token_hash, status, expires_at) "
        "VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days')",
        (foreign_session, foreign_user, org_b, hash_token("foreign-access")),
    )
    conn.commit()

    try:
        with pytest.raises(PermissionError, match="does not belong"):
            AuthService.switch_organization(cur, user_id, org_b, foreign_session)
    finally:
        cur.execute("DELETE FROM user_sessions WHERE id = %s", (foreign_session,))
        cur.execute("DELETE FROM users WHERE id = %s", (foreign_user,))
        conn.commit()


def test_p0_refresh_token_is_rotated_and_old_token_replay_fails(auth_env):
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    session_id = str(uuid.uuid4())
    access = encode_access_token(user_id, session_id, org_a, "RETAILER_OWNER")
    old_refresh = generate_refresh_token()

    cur.execute(
        """
        INSERT INTO user_sessions
            (id, user_id, active_organization_id, token_hash, refresh_token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, %s, 'ACTIVE', now() + interval '30 days')
        """,
        (session_id, user_id, org_a, hash_token(access), hash_token(old_refresh)),
    )
    conn.commit()

    first = AuthService.refresh_access_token(cur, old_refresh)
    assert first["access_token"]
    assert first["refresh_token"]
    assert first["refresh_token"] != old_refresh

    cur.execute(
        "SELECT refresh_token_hash FROM user_sessions WHERE id = %s",
        (session_id,),
    )
    assert cur.fetchone()["refresh_token_hash"] == hash_token(first["refresh_token"])

    with pytest.raises(InvalidRefreshTokenError):
        AuthService.refresh_access_token(cur, old_refresh)

    cur.execute("DELETE FROM user_sessions WHERE id = %s", (session_id,))
    conn.commit()


def test_p0_verify_otp_rejects_user_mismatch_for_same_phone(auth_env):
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    attacker_user = str(uuid.uuid4())
    phone = auth_env["phone"] if "phone" in auth_env else "+989161110099"

    if phone == "+989161110099":
        cur.execute(
            "SELECT phone_number FROM users WHERE id = %s",
            (user_id,),
        )
        phone = cur.fetchone()["phone_number"]

    otp_id = str(uuid.uuid4())
    cur.execute(
        """
        INSERT INTO otp_challenges
            (id, phone_number, code_hash, purpose, ip_address, attempts_count, max_attempts, status, expires_at)
        VALUES (%s, %s, %s, 'LOGIN', '10.0.0.99', 0, 5, 'PENDING', now() + interval '2 minutes')
        """,
        (otp_id, phone, store_otp_hash("1234")),
    )
    conn.commit()

    try:
        with pytest.raises(PermissionError, match="identity"):
            AuthService.verify_otp(cur, phone, "1234", attacker_user, org_a)
    finally:
        cur.execute("DELETE FROM otp_challenges WHERE id = %s", (otp_id,))
        conn.rollback()


# =========================================================
# Remediation: active principal enforcement for bearer and refresh tokens
# =========================================================

def _insert_active_session(cur, user_id, org_id):
    sess_id = str(uuid.uuid4())
    access_token = encode_access_token(user_id, sess_id, org_id, "RETAILER_OWNER")
    refresh_token = generate_refresh_token()
    cur.execute(
        """
        INSERT INTO user_sessions
            (id, user_id, active_organization_id, token_hash, refresh_token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, %s, 'ACTIVE', now() + interval '30 days')
        """,
        (sess_id, user_id, org_id, hash_token(access_token), hash_token(refresh_token)),
    )
    return sess_id, access_token, refresh_token


def test_access_token_rejects_inactive_user(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id, access_token, _ = _insert_active_session(cur, user_id, org_a)
    conn.commit()

    try:
        cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s;", (user_id,))
        conn.commit()
        with pytest.raises(AuthError, match="inactive"):
            validate_access_token(cur, access_token)
    finally:
        cur.execute("UPDATE users SET is_active = TRUE WHERE id = %s;", (user_id,))
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


def test_access_token_rejects_inactive_organization(auth_env):
    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id, access_token, _ = _insert_active_session(cur, user_id, org_a)
    conn.commit()

    try:
        cur.execute("UPDATE organizations SET status = 'SUSPENDED' WHERE id = %s;", (org_a,))
        conn.commit()
        with pytest.raises(AuthError, match="Organization is not active"):
            validate_access_token(cur, access_token)
    finally:
        cur.execute("UPDATE organizations SET status = 'ACTIVE' WHERE id = %s;", (org_a,))
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


def test_refresh_token_rejects_inactive_user(auth_env):
    from scripts.auth_boundary import InvalidRefreshTokenError
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id, _, refresh_token = _insert_active_session(cur, user_id, org_a)
    conn.commit()

    try:
        cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s;", (user_id,))
        conn.commit()
        with pytest.raises(InvalidRefreshTokenError, match="inactive"):
            AuthService.refresh_access_token(cur, refresh_token)
    finally:
        cur.execute("UPDATE users SET is_active = TRUE WHERE id = %s;", (user_id,))
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


def test_refresh_token_rejects_inactive_organization(auth_env):
    from scripts.auth_boundary import InvalidRefreshTokenError
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    sess_id, _, refresh_token = _insert_active_session(cur, user_id, org_a)
    conn.commit()

    try:
        cur.execute("UPDATE organizations SET status = 'SUSPENDED' WHERE id = %s;", (org_a,))
        conn.commit()
        with pytest.raises(InvalidRefreshTokenError, match="Organization is not active"):
            AuthService.refresh_access_token(cur, refresh_token)
    finally:
        cur.execute("UPDATE organizations SET status = 'ACTIVE' WHERE id = %s;", (org_a,))
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (sess_id,))
        conn.commit()


# =========================================================
# P0 REGRESSION: DIRECT AUTHORIZATION / ORG SWITCH PRINCIPAL STATE
# =========================================================
def test_authorize_action_rejects_inactive_user(auth_env):
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]

    cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s;", (user_id,))
    conn.commit()
    try:
        with pytest.raises(PermissionError, match="inactive"):
            AuthService.authorize_action(
                cur,
                user_id,
                org_a,
                ["RETAILER_OWNER"],
            )
    finally:
        cur.execute("UPDATE users SET is_active = TRUE WHERE id = %s;", (user_id,))
        conn.commit()


def test_switch_organization_rejects_inactive_user(auth_env):
    from scripts.domain_services import AuthService

    conn = auth_env["conn"]
    cur = auth_env["cur"]
    user_id = auth_env["user_id"]
    org_a = auth_env["org_a"]
    org_b = auth_env["org_b"]

    session_id = str(uuid.uuid4())
    access = encode_access_token(user_id, session_id, org_a, "RETAILER_OWNER")
    cur.execute(
        """
        INSERT INTO user_sessions
            (id, user_id, active_organization_id, token_hash, status, expires_at)
        VALUES (%s, %s, %s, %s, 'ACTIVE', now() + interval '30 days')
        """,
        (session_id, user_id, org_a, hash_token(access)),
    )
    cur.execute("UPDATE users SET is_active = FALSE WHERE id = %s;", (user_id,))
    conn.commit()

    try:
        with pytest.raises(PermissionError, match="inactive"):
            AuthService.switch_organization(cur, user_id, org_b, session_id)
    finally:
        cur.execute("UPDATE users SET is_active = TRUE WHERE id = %s;", (user_id,))
        cur.execute("DELETE FROM user_sessions WHERE id = %s;", (session_id,))
        conn.commit()
