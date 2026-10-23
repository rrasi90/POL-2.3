"""Live HTTP transport behaviour against a real uvicorn process (TODO-074).

Unlike the TestClient suites, these tests speak HTTP over a socket to a real
server process so that connection failures, read timeouts, malformed payloads
and error envelopes are exercised at the transport layer.
"""

from __future__ import annotations

import http.client
import json
import os
import socket
import subprocess
import sys
import threading
import time

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _server_env(port: int) -> dict:
    env = dict(os.environ)
    env.setdefault("ENVIRONMENT", "test")
    env.setdefault("POL_API_DB_NAME", "pol_test")
    env.setdefault("POL_API_DB_HOST", "127.0.0.1")
    env.setdefault("POL_API_DB_PORT", env.get("POL_PG_PORT", "5432"))
    env.setdefault(
        "POL_JWT_SECRET",
        "test-secret-key-for-auth-contract-tests-only-32bytes!!",
    )
    env["PYTHONIOENCODING"] = "utf-8"
    env["POL_LIVE_PORT"] = str(port)
    return env


class _Server:
    def __init__(self):
        self.port = _free_port()
        self.proc = None
        self.logs = []

    def start(self):
        self.proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "scripts.api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--log-level",
                "warning",
            ],
            cwd=REPO_ROOT,
            env=_server_env(self.port),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        deadline = time.time() + 45
        while time.time() < deadline:
            if self.proc.poll() is not None:
                output = self.proc.stdout.read() if self.proc.stdout else ""
                raise RuntimeError(f"uvicorn exited early:\n{output}")
            try:
                status, _ = self.request("GET", "/healthz", timeout=1.0)
                if status == 200:
                    return
            except OSError:
                time.sleep(0.25)
        raise TimeoutError("uvicorn did not become ready in 45s")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=10)
        if self.proc and self.proc.stdout:
            self.logs = self.proc.stdout.read().splitlines()
            self.proc.stdout.close()

    def request(self, method, path, body=None, headers=None, timeout=10.0):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=timeout)
        try:
            payload = None
            if body is not None:
                payload = body if isinstance(body, (bytes, str)) else json.dumps(body)
            conn.request(method, path, body=payload, headers=headers or {})
            response = conn.getresponse()
            raw = response.read()
            return response.status, raw
        finally:
            conn.close()


@pytest.fixture(scope="module")
def live_server():
    server = _Server()
    server.start()
    try:
        yield server
    finally:
        server.stop()


def _envelope(raw):
    return json.loads(raw.decode("utf-8"))


class TestLiveTransportErrors:
    def test_error_envelopes_are_never_silent_success(self, live_server):
        status, raw = live_server.request("GET", "/api/v1/baskets/current")
        body = _envelope(raw)
        assert status == 401
        assert body["success"] is False
        assert body["error"]["code"] == "INVALID_ACCESS_TOKEN"

    def test_unknown_route_returns_enveloped_404(self, live_server):
        status, raw = live_server.request("GET", "/api/v1/does-not-exist")
        assert status in (404, 405)
        body = _envelope(raw)
        assert body["success"] is False
        assert body["error"]["code"] in {"NOT_FOUND", "METHOD_NOT_ALLOWED", "HTTP_ERROR"}

    def test_malformed_json_body_returns_validation_error(self, live_server):
        status, raw = live_server.request(
            "POST",
            "/api/v1/auth/request-otp",
            body=b'{"phone_number": "0912',
            headers={"Content-Type": "application/json"},
        )
        body = _envelope(raw)
        assert status == 422
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_wrong_content_type_is_rejected(self, live_server):
        status, raw = live_server.request(
            "POST",
            "/api/v1/auth/request-otp",
            body="phone_number=09121234567",
            headers={"Content-Type": "text/plain"},
        )
        body = _envelope(raw)
        assert status == 422
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_missing_required_field_is_request_validation_error(self, live_server):
        status, raw = live_server.request(
            "POST",
            "/api/v1/auth/request-otp",
            body={"phone_number": "0912"},
            headers={"Content-Type": "application/json"},
        )
        body = _envelope(raw)
        assert status == 422
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_garbage_access_token_is_rejected_on_a_real_socket(self, live_server):
        status, raw = live_server.request(
            "GET",
            "/api/v1/baskets/current",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        body = _envelope(raw)
        assert status == 401
        assert body["success"] is False


class TestNetworkFailureContract:
    def test_connection_refused_raises_and_is_not_retried(self):
        port = _free_port()
        attempts = 0
        with pytest.raises(OSError):
            attempts += 1
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
            try:
                conn.request("GET", "/healthz")
                conn.getresponse()
            finally:
                conn.close()
        assert attempts == 1, "network failures must surface immediately, not retry"

    def test_read_timeout_raises_once(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        held = []

        def _hold():
            try:
                client, _ = listener.accept()
                held.append(client)
                time.sleep(3)
            except OSError:
                pass
            finally:
                for client in held:
                    client.close()
                listener.close()

        thread = threading.Thread(target=_hold, daemon=True)
        thread.start()

        attempts = 0
        start = time.time()
        with pytest.raises((socket.timeout, TimeoutError, OSError)):
            attempts += 1
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
            try:
                conn.request("GET", "/healthz")
                conn.getresponse()
            finally:
                conn.close()
        elapsed = time.time() - start
        assert attempts == 1
        assert elapsed < 2.5, f"timeout should fire promptly, took {elapsed:.2f}s"

    def test_no_silent_success_on_unreachable_host(self):
        port = _free_port()
        payloads = []
        with pytest.raises(OSError):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=2.0)
            try:
                conn.request("POST", "/api/v1/baskets", body="{}")
                response = conn.getresponse()
                payloads.append(response.status)
            finally:
                conn.close()
        assert payloads == [], "an unreachable mutation must never look successful"
