"""Notification provider adapter structure with mock/sandbox handling.

Stage 33 — provides the interface and mock adapters for external notification
delivery. No live provider integration; concrete providers are added later
after the procurement decision is finalised.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProviderResult:
    success: bool
    provider_message_id: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class NotificationProvider(abc.ABC):
    """Abstract base for all notification delivery providers."""

    @abc.abstractmethod
    def send(
        self,
        channel: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> ProviderResult:
        ...


class MockProvider(NotificationProvider):
    """Deterministic provider that always succeeds.  Safe for unit tests."""

    def send(
        self,
        channel: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> ProviderResult:
        return ProviderResult(
            success=True,
            provider_message_id=str(uuid.uuid4()),
            metadata={"channel": channel, "recipient": recipient},
        )


class SandboxProvider(NotificationProvider):
    """Simulates latency and configurable failure rates for integration tests."""

    def __init__(
        self,
        delay_seconds: float = 0.0,
        failure_rate: float = 0.0,
        seed: int | None = None,
    ) -> None:
        self.delay_seconds = delay_seconds
        self.failure_rate = failure_rate
        self._rng = __import__("random").Random(seed)

    def send(
        self,
        channel: str,
        recipient: str,
        subject: str,
        body: str,
    ) -> ProviderResult:
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)

        if self._rng.random() < self.failure_rate:
            return ProviderResult(
                success=False,
                error="sandbox-simulated-failure",
                metadata={"channel": channel, "recipient": recipient},
            )

        return ProviderResult(
            success=True,
            provider_message_id=str(uuid.uuid4()),
            metadata={"channel": channel, "recipient": recipient},
        )


_REGISTRY: dict[str, type[NotificationProvider]] = {
    "mock": MockProvider,
    "sandbox": SandboxProvider,
}


def get_provider(name: str = "mock", **kwargs) -> NotificationProvider:
    """Factory that returns a named provider instance.

    Extra *kwargs* are forwarded to the provider constructor.  Unknown
    provider names raise ``ValueError``.
    """
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown notification provider: {name!r}")
    return cls(**kwargs)


def register_provider(name: str, cls: type[NotificationProvider]) -> None:
    """Register a custom provider class for use with :func:`get_provider`."""
    _REGISTRY[name] = cls
