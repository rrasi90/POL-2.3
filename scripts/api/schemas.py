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

    
class BasketItemRequest(APIBaseModel):
    product_id: UUID
    requested_quantity: int = Field(gt=0)
    pack_quantity: int = Field(default=1, gt=0)
    expected_version: int = Field(ge=1)


class CheckoutRequest(APIBaseModel):
    allocation_plan_id: UUID
    delivery_address: str = Field(min_length=5, max_length=1000)
    preferred_payment_method: Literal[
        "CASH_ON_DELIVERY",
        "POS_DRIVER",
        "DIRECT_BANK_TRANSFER",
        "CHEQUE_SAYYAD",
        "ONLINE_MOCK",
    ]


class VendorOrderRejectRequest(APIBaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class VendorPartialAcceptanceItemRequest(APIBaseModel):
    order_item_id: UUID
    accepted_quantity: int = Field(gt=0)
    reason: str | None = Field(default=None, max_length=255)


class VendorPartialAcceptanceProposalRequest(APIBaseModel):
    items: list[VendorPartialAcceptanceItemRequest] = Field(min_length=1)


class RetailerPartialAcceptanceDeclineRequest(APIBaseModel):
    reason: str | None = Field(default=None, max_length=1000)


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


class VendorCatalogCreateRequest(APIBaseModel):
    vendor_sku: str = Field(min_length=1, max_length=100)
    product_id: UUID | None = None
    candidate_id: UUID | None = None
    packaging_unit: str = Field(default="CARTON", max_length=30)
    pack_quantity: int = Field(default=12, gt=0)
    sales_unit: str = Field(default="CARTON", max_length=30)
    initial_price_toman: int | None = Field(default=None, gt=0)
    moq: int = Field(default=1, ge=1)


class VendorCatalogUpdateRequest(APIBaseModel):
    packaging_unit: str | None = Field(default=None, max_length=30)
    pack_quantity: int | None = Field(default=None, gt=0)
    sales_unit: str | None = Field(default=None, max_length=30)
    moq: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class VendorPriceSetRequest(APIBaseModel):
    price_toman: int = Field(gt=0)


class VendorInventoryAdjustRequest(APIBaseModel):
    new_physical_quantity: int = Field(ge=0)
    reason: str = Field(default="MANUAL_EDIT", max_length=50)


class DailyInventoryConfirmRequest(APIBaseModel):
    confirmation_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class DailyInventoryChangeItemRequest(APIBaseModel):
    vendor_product_id: UUID
    declared_quantity: int = Field(ge=0)


class DailyInventoryConfirmWithChangesRequest(APIBaseModel):
    confirmation_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    changes: list[DailyInventoryChangeItemRequest] = Field(min_length=1)


class OrderQueryParams(APIBaseModel):
    status: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class DispatchRequest(APIBaseModel):
    driver_name: str | None = Field(default=None, max_length=100)
    vehicle_plate: str | None = Field(default=None, max_length=20)
    driver_phone: str | None = Field(default=None, max_length=32)


class DeliveryConfirmRequest(APIBaseModel):
    recipient_name: str | None = Field(default=None, max_length=200)
    otp_code: str | None = Field(default=None, pattern=r"^\d{4}$")
    proof_type: str = Field(default="OTP_CODE", max_length=30)
    proof_media_id: str | None = Field(default=None, max_length=64)
    issue_reported: str | None = Field(default=None, max_length=500)


class DeliveryExceptionReportRequest(APIBaseModel):
    delivery_id: str = Field(min_length=1, max_length=64)
    order_id: str = Field(min_length=1, max_length=64)
    exception_type: str = Field(min_length=1, max_length=30)
    description: str | None = Field(default=None, max_length=2000)


class DeliveryExceptionResolveRequest(APIBaseModel):
    resolution_type: str = Field(min_length=1, max_length=30)
    resolution_note: str | None = Field(default=None, max_length=2000)


class DeliveryExceptionEscalateRequest(APIBaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class NotificationPreferenceUpdateRequest(APIBaseModel):
    event_name: str = Field(min_length=1, max_length=100)
    channel: str = Field(min_length=1, max_length=10)
    is_enabled: bool


class FieldTaskCreateRequest(APIBaseModel):
    task_type: str = Field(min_length=1, max_length=30)
    assigned_to_user_id: str = Field(min_length=1, max_length=64)
    retailer_id: str | None = Field(default=None, max_length=64)
    vendor_id: str | None = Field(default=None, max_length=64)
    notes: str | None = Field(default=None, max_length=2000)


class FieldTaskUpdateRequest(APIBaseModel):
    status: str | None = Field(default=None, max_length=20)
    notes: str | None = Field(default=None, max_length=2000)


class ReturnItemRequest(APIBaseModel):
    order_item_id: UUID
    quantity: int = Field(gt=0)
    reason_code: str = Field(default="OTHER", max_length=30)
    unit_refund_amount_toman: int | None = Field(default=None, ge=0)


class ReturnRequestRequest(APIBaseModel):
    items: list[ReturnItemRequest] = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=1000)
    idempotency_key: str = Field(min_length=1, max_length=128)
    claimed_refund_amount_toman: int = Field(ge=0)


class ReturnTransitionRequest(APIBaseModel):
    target_status: str = Field(min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=1000)
    approved_refund_amount_toman: int | None = Field(default=None, ge=0)


class DisputeOpenRequest(APIBaseModel):
    description: str = Field(min_length=1, max_length=2000)
    evidence_media_id: UUID | None = None


class PaymentEvidenceRequest(APIBaseModel):
    evidence_type: Literal[
        "BANK_REFERENCE", "POS_REFERENCE", "RECEIPT_IMAGE",
        "VENDOR_CONFIRMATION", "RETAILER_CONFIRMATION",
    ]
    reference_number: str = Field(min_length=1, max_length=255)
    amount_toman: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=2000)


class PaymentVerifyRequest(APIBaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class ReconciliationCaseResolveRequest(APIBaseModel):
    resolution_note: str | None = Field(default=None, max_length=2000)


class SupportCaseCreateRequest(APIBaseModel):
    case_type: str = Field(min_length=1, max_length=50)
    subject: str = Field(min_length=1, max_length=500)
    related_order_id: str | None = Field(default=None, max_length=64)
    priority: str = Field(default="NORMAL", max_length=20)


class SupportCaseMessageRequest(APIBaseModel):
    message_text: str = Field(min_length=1, max_length=5000)


class SupportCaseTransitionRequest(APIBaseModel):
    target_status: str = Field(min_length=1, max_length=30)
    resolution_code: str | None = Field(default=None, max_length=50)
    resolution_note: str | None = Field(default=None, max_length=2000)


class ReferralCreateRequest(APIBaseModel):
    referred_retailer_id: UUID
    referral_code: str = Field(min_length=1, max_length=32)


class ReferralRedeemRequest(APIBaseModel):
    pass
