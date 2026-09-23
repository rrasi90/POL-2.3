"""Unit tests for the notification provider adapter structure — Stage 33."""

from __future__ import annotations

import pytest

from notification_providers import (
    MockProvider,
    NotificationProvider,
    ProviderResult,
    SandboxProvider,
    get_provider,
    register_provider,
)


# ---------------------------------------------------------------------------
# MockProvider
# ---------------------------------------------------------------------------

class TestMockProvider:
    def test_always_succeeds(self):
        p = MockProvider()
        result = p.send("SMS", "+989160000000", "Hi", "Hello")
        assert result.success is True
        assert result.provider_message_id is not None
        assert result.error is None

    def test_metadata_contains_channel_and_recipient(self):
        p = MockProvider()
        result = p.send("PUSH", "token-abc", "Subject", "Body")
        assert result.metadata["channel"] == "PUSH"
        assert result.metadata["recipient"] == "token-abc"


# ---------------------------------------------------------------------------
# SandboxProvider
# ---------------------------------------------------------------------------

class TestSandboxProvider:
    def test_success_under_zero_failure_rate(self):
        p = SandboxProvider(failure_rate=0.0, seed=42)
        result = p.send("SMS", "+989160000000", "Sub", "Bod")
        assert result.success is True
        assert result.provider_message_id is not None

    def test_can_simulate_failure(self):
        p = SandboxProvider(failure_rate=1.0, seed=42)
        result = p.send("SMS", "+989160000000", "Sub", "Bod")
        assert result.success is False
        assert result.error == "sandbox-simulated-failure"


# ---------------------------------------------------------------------------
# ProviderResult
# ---------------------------------------------------------------------------

class TestProviderResult:
    def test_defaults(self):
        r = ProviderResult(success=True)
        assert r.provider_message_id is None
        assert r.error is None
        assert r.metadata == {}

    def test_immutable(self):
        r = ProviderResult(success=True, provider_message_id="m-1")
        with pytest.raises(AttributeError):
            r.success = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Factory / registry
# ---------------------------------------------------------------------------

class TestProviderFactory:
    def test_returns_mock_by_default(self):
        p = get_provider()
        assert isinstance(p, MockProvider)

    def test_returns_sandbox(self):
        p = get_provider("sandbox", delay_seconds=0.0)
        assert isinstance(p, SandboxProvider)

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown notification provider"):
            get_provider("nonexistent")

    def test_register_custom_provider(self):
        class _Custom(NotificationProvider):
            def send(self, channel, recipient, subject, body):
                return ProviderResult(success=True, provider_message_id="custom-1")

        register_provider("custom", _Custom)
        p = get_provider("custom")
        assert isinstance(p, _Custom)
        result = p.send("EMAIL", "a@b.com", "S", "B")
        assert result.provider_message_id == "custom-1"


# ---------------------------------------------------------------------------
# Contract — all providers must satisfy the ABC
# ---------------------------------------------------------------------------

class TestProviderContract:
    def test_mock_is_subclass(self):
        assert issubclass(MockProvider, NotificationProvider)

    def test_sandbox_is_subclass(self):
        assert issubclass(SandboxProvider, NotificationProvider)
