"""Pydantic transport schemas for the current HTTP slice."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequestOTPRequest(APIBaseModel):
    mobile_number: str = Field(min_length=7, max_length=32)
    client_fingerprint: str | None = Field(default=None, max_length=128)


class VerifyOTPRequest(APIBaseModel):
    mobile_number: str = Field(min_length=7, max_length=32)
    otp_code: str = Field(pattern=r"^\d{4}$")
    device_info: dict[str, Any] | None = None


class RefreshTokenRequest(APIBaseModel):
    refresh_token: str = Field(min_length=20, max_length=512)


class SwitchOrganizationRequest(APIBaseModel):
    target_organization_id: UUID


class ProfileUpdateRequest(APIBaseModel):
    display_name: str | None = None
    email: str | None = None
    preferred_language: str | None = None
    timezone: str | None = None
    bio: str | None = None
    avatar_media_asset_id: str | None = Field(default=None, max_length=64)


class MembershipProfileUpdateRequest(APIBaseModel):
    display_name_override: str | None = None
    title: str | None = None
    default_contact_channel: Literal["IN_APP", "PUSH", "SMS"] | None = None
    locale_override: Literal["fa-IR", "en-US"] | None = None
    preferences: dict[str, Any] | None = None
