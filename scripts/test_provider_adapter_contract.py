"""TODO-133 - provider adapter timeouts and fail-closed response handling.

The adapters are the only place that talks to an external SMS/PUSH provider.
They must never:

* call out without explicit endpoint configuration,
* swallow a timeout or a provider 5xx as success,
* treat an unverifiable 2xx body as a delivered message.

Duplicate protection relies on the ``Idempotency-Key`` header plus a stable
request fingerprint, both asserted here.
"""

from __future__ import annotations

import pytest
import requests

from scripts import provider_adapters
from scripts.provider_adapters import (
    GenericPushProviderAdapter,
    GenericSmsProviderAdapter,
    ProviderConfigurationError,
    ProviderPermanentError,
    ProviderTransientError,
    build_adapter,
)


class FakeResponse:
    def __init__(self, status_code: int, *, json_body=None, text_body: str | None = None, headers=None):
        self.status_code = status_code
        self.headers = headers or {}
        self._json_body = json_body
        self._text_body = text_body

    def json(self):
        if self._json_body is None:
            raise ValueError("no json body")
        return self._json_body


def _adapter(monkeypatch, *, token: str | None = "secret-token", channel: str = "SMS"):
    monkeypatch.setenv("POL_SMS_ENDPOINT", "https://sms.example.test/send")
    monkeypatch.setenv("POL_PUSH_ENDPOINT", "https://push.example.test/send")
    if token is None:
        monkeypatch.delenv("POL_SMS_TOKEN", raising=False)
        monkeypatch.delenv("POL_PUSH_TOKEN", raising=False)
    else:
        monkeypatch.setenv("POL_SMS_TOKEN", token)
        monkeypatch.setenv("POL_PUSH_TOKEN", token)
    return build_adapter(channel)


def test_missing_endpoint_is_a_configuration_error(monkeypatch):
    monkeypatch.delenv("POL_SMS_ENDPOINT", raising=False)
    with pytest.raises(ProviderConfigurationError):
        GenericSmsProviderAdapter("GENERIC_SMS", "POL_SMS_ENDPOINT", "POL_SMS_TOKEN")


def test_2xx_with_message_id_is_a_success(monkeypatch):
    adapter = _adapter(monkeypatch)

    def fake_post(endpoint, json, headers, timeout):
        assert endpoint == "https://sms.example.test/send"
        assert timeout == 10.0
        assert headers["Idempotency-Key"] == "idem-1"
        assert headers["Authorization"] == "Bearer secret-token"
        return FakeResponse(200, json_body={"id": "prov-42", "status": "queued"})

    monkeypatch.setattr(provider_adapters.requests, "post", fake_post)
    result = adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem-1")
    assert result.provider == "GENERIC_SMS"
    assert result.provider_message_id == "prov-42"
    assert result.provider_code == "200"
    assert result.metadata["response"]["status"] == "queued"


def test_header_message_id_is_accepted_even_with_a_non_json_body(monkeypatch):
    adapter = _adapter(monkeypatch)
    monkeypatch.setattr(
        provider_adapters.requests,
        "post",
        lambda *a, **k: FakeResponse(202, text_body="OK", headers={"X-Message-Id": "hdr-9"}),
    )
    result = adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem-2")
    assert result.provider_message_id == "hdr-9"
    assert result.provider_code == "202"


def test_unverifiable_2xx_is_not_reported_as_success(monkeypatch):
    adapter = _adapter(monkeypatch)
    monkeypatch.setattr(provider_adapters.requests, "post", lambda *a, **k: FakeResponse(200, text_body="OK"))
    try:
        adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem-3")
    except ProviderTransientError as exc:
        assert "invalid body" in str(exc)
    else:
        raise AssertionError("a 2xx without any message id must not be treated as delivered")


def test_2xx_json_array_is_not_treated_as_success(monkeypatch):
    adapter = _adapter(monkeypatch)
    monkeypatch.setattr(provider_adapters.requests, "post", lambda *a, **k: FakeResponse(200, json_body=[1, 2, 3]))
    try:
        adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem-4")
    except ProviderTransientError:
        pass
    else:
        raise AssertionError("an unexpected body type must fail closed")


def test_rate_limit_and_5xx_are_transient(monkeypatch):
    adapter = _adapter(monkeypatch)
    for status in (429, 500, 503):
        monkeypatch.setattr(provider_adapters.requests, "post", lambda *a, **k: FakeResponse(status))
        try:
            adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem")
        except ProviderTransientError:
            continue
        raise AssertionError(f"HTTP {status} must be transient")


def test_4xx_is_permanent(monkeypatch):
    adapter = _adapter(monkeypatch)
    monkeypatch.setattr(provider_adapters.requests, "post", lambda *a, **k: FakeResponse(404))
    try:
        adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem")
    except ProviderPermanentError:
        return
    raise AssertionError("HTTP 404 must be permanent")


def test_timeout_is_transient_and_never_success(monkeypatch):
    adapter = _adapter(monkeypatch)

    def raise_timeout(*args, **kwargs):
        raise requests.Timeout("read timed out")

    monkeypatch.setattr(provider_adapters.requests, "post", raise_timeout)
    try:
        adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem")
    except ProviderTransientError:
        return
    raise AssertionError("a timeout must never be treated as a sent message")


def test_no_authorization_header_without_a_token(monkeypatch):
    adapter = _adapter(monkeypatch, token=None)
    seen = {}

    def fake_post(endpoint, json, headers, timeout):
        seen.update(headers)
        return FakeResponse(200, json_body={"id": "no-token-1"})

    monkeypatch.setattr(provider_adapters.requests, "post", fake_post)
    adapter.send(phone_number="+989120000000", title="t", body="b", idempotency_key="idem-5")
    assert "Authorization" not in seen


def test_request_fingerprint_is_stable_and_channel_scoped(monkeypatch):
    sms = _adapter(monkeypatch, channel="SMS")
    push = _adapter(monkeypatch, channel="PUSH")
    monkeypatch.setattr(
        provider_adapters.requests, "post", lambda *a, **k: FakeResponse(200, json_body={"id": "fp-1"})
    )
    first = sms.send(phone_number="+989120000000", title="t", body="b", idempotency_key="k1")
    second = sms.send(phone_number="+989120000000", title="t", body="b", idempotency_key="k1")
    changed = sms.send(phone_number="+989120000000", title="t", body="b2", idempotency_key="k1")
    pushed = push.send(
        push_token="device-1", title="t", body="b", data={"a": 1}, idempotency_key="k1"
    )
    assert first.metadata["request_fingerprint"] == second.metadata["request_fingerprint"]
    assert first.metadata["request_fingerprint"] != pushed.metadata["request_fingerprint"]
    assert first.metadata["request_fingerprint"] != changed.metadata["request_fingerprint"]
