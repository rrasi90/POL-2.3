"""Provider-neutral external notification adapters.

POL does not hard-code a provider before the operational/provider procurement
choice is made. Concrete adapters implement the same deterministic contract.
No adapter performs a call without explicit endpoint/credential configuration.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass

import requests


class ProviderConfigurationError(RuntimeError):
    pass


class ProviderTransientError(RuntimeError):
    pass


class ProviderPermanentError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    provider_message_id: str | None
    provider_code: str | None
    metadata: dict


class BaseHttpProviderAdapter:
    channel = ""

    def __init__(self, provider_name: str, endpoint_env: str, token_env: str | None = None, timeout_seconds: float = 10.0):
        self.provider_name = provider_name
        self.endpoint = os.getenv(endpoint_env)
        self.token = os.getenv(token_env) if token_env else None
        self.timeout_seconds = timeout_seconds
        if not self.endpoint:
            raise ProviderConfigurationError(f"{provider_name}: missing endpoint configuration")

    def _headers(self, idempotency_key: str):
        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _post(self, payload: dict, idempotency_key: str) -> ProviderResult:
        request_fingerprint = hashlib.sha256(
            (self.provider_name + "|" + self.channel + "|" + repr(sorted(payload.items()))).encode("utf-8")
        ).hexdigest()
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self._headers(idempotency_key),
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise ProviderTransientError(str(exc)) from exc

        provider_message_id = response.headers.get("X-Message-Id")
        provider_code = str(response.status_code)
        if 200 <= response.status_code < 300:
            body: dict = {}
            body_was_invalid = False
            try:
                parsed = response.json()
            except ValueError:
                parsed = None
                body_was_invalid = True
            if isinstance(parsed, dict):
                body = parsed
            elif parsed is not None:
                body_was_invalid = True
            provider_message_id = provider_message_id or body.get("message_id") or body.get("id")
            if not provider_message_id:
                detail = "an invalid body" if body_was_invalid else "no message id"
                raise ProviderTransientError(
                    f"{self.provider_name} returned HTTP {response.status_code} with {detail}"
                )
            return ProviderResult(
                provider=self.provider_name,
                provider_message_id=str(provider_message_id) if provider_message_id else None,
                provider_code=provider_code,
                metadata={"request_fingerprint": request_fingerprint, "response": body},
            )
        if response.status_code == 429 or response.status_code >= 500:
            raise ProviderTransientError(f"{self.provider_name} returned HTTP {response.status_code}")
        raise ProviderPermanentError(f"{self.provider_name} returned HTTP {response.status_code}")


class GenericSmsProviderAdapter(BaseHttpProviderAdapter):
    channel = "SMS"

    def send(self, *, phone_number: str, title: str, body: str, idempotency_key: str):
        return self._post(
            {"to": phone_number, "title": title, "body": body, "request_id": idempotency_key},
            idempotency_key,
        )


class GenericPushProviderAdapter(BaseHttpProviderAdapter):
    channel = "PUSH"

    def send(self, *, push_token: str, title: str, body: str, data: dict, idempotency_key: str):
        return self._post(
            {"token": push_token, "title": title, "body": body, "data": data, "request_id": idempotency_key},
            idempotency_key,
        )


def build_adapter(channel: str):
    if channel == "SMS":
        return GenericSmsProviderAdapter(
            provider_name=os.getenv("POL_SMS_PROVIDER", "GENERIC_SMS"),
            endpoint_env="POL_SMS_ENDPOINT",
            token_env="POL_SMS_TOKEN",
        )
    if channel == "PUSH":
        return GenericPushProviderAdapter(
            provider_name=os.getenv("POL_PUSH_PROVIDER", "GENERIC_PUSH"),
            endpoint_env="POL_PUSH_ENDPOINT",
            token_env="POL_PUSH_TOKEN",
        )
    raise ProviderConfigurationError(f"Unsupported provider channel: {channel}")
