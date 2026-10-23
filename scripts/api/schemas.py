"""Pydantic transport schemas for the current HTTP slice."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator

from scripts.operational_config import MAX_BULK_ITEMS

INT4_MAX = 2_147_483_647

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _uuid_string(value: str) -> str:
    """Validate a UUID-shaped reference while keeping the transport type a string."""
    try:
        return str(UUID(str(value)))
    except (TypeError, ValueError) as exc:
        raise ValueError("must be a valid UUID") from exc


UuidString = Annotated[str, AfterValidator(_uuid_string)]


class APIBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def _reject_boolean_and_overflowing_integers(cls, value, info):
        if isinstance(value, bool):
            annotation = cls.model_fields[info.field_name].annotation
            if "bool" not in str(annotation):
                raise ValueError(f"{info.field_name} must be an integer, not a boolean")
            return value
        if isinstance(value, int) and not isinstance(value, bool):
            annotation = str(cls.model_fields[info.field_name].annotation)
            if "str" not in annotation and abs(value) > INT4_MAX:
                raise ValueError(
                    f"{info.field_name} exceeds the supported 32-bit integer range"
                )
        return value

    @field_validator("*", mode="after")
    @classmethod
    def _reject_control_characters(cls, value):
        if isinstance(value, str) and CONTROL_CHARACTERS.search(value):
            raise ValueError("control characters are not allowed in text fields")
        return value


class RequestOTPRequest(APIBaseModel):
    mobile_number: str = Field(min_length=8, max_length=16, pattern=r"^\+[1-9][0-9]{7,14}$")
    client_fingerprint: str | None = Field(default=None, max_length=128)


class VerifyOTPRequest(APIBaseModel):
    mobile_number: str = Field(min_length=8, max_length=16, pattern=r"^\+[1-9][0-9]{7,14}$")
    otp_code: str = Field(pattern=r"^[0-9]{4}$")
    device_info: dict[str, Any] | None = None
    client_platform: Literal["web", "mobile"] | None = None


class RefreshTokenRequest(APIBaseModel):
    refresh_token: str | None = Field(default=None, min_length=20, max_length=512)


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
    items: list[VendorPartialAcceptanceItemRequest] = Field(min_length=1, max_length=MAX_BULK_ITEMS)


class RetailerPartialAcceptanceDeclineRequest(APIBaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class PrivacyExportRequest(APIBaseModel):
    include_activity_counts: bool = True

class ProfileUpdateRequest(APIBaseModel):
    display_name: str | None = None
    email: str | None = None
    preferred_language: str | None = None
    timezone: str | None = None
    bio: str | None = None
    avatar_media_asset_id: UuidString | None = Field(default=None, max_length=64)


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
    confirmation_date: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

    @field_validator("confirmation_date")
    @classmethod
    def _calendar_valid_date(cls, value: str) -> str:
        date.fromisoformat(value)
        return value


class DailyInventoryChangeItemRequest(APIBaseModel):
    vendor_product_id: UUID
    declared_quantity: int = Field(ge=0)


class DailyInventoryConfirmWithChangesRequest(APIBaseModel):
    confirmation_date: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    changes: list[DailyInventoryChangeItemRequest] = Field(min_length=1, max_length=MAX_BULK_ITEMS)

    @field_validator("confirmation_date")
    @classmethod
    def _calendar_valid_date(cls, value: str) -> str:
        date.fromisoformat(value)
        return value


class OrderQueryParams(APIBaseModel):
    status: str | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)


class DispatchRequest(APIBaseModel):
    driver_name: str | None = Field(default=None, max_length=100)
    vehicle_plate: str | None = Field(default=None, max_length=20)
    driver_phone: str | None = Field(default=None, max_length=32)


class DeliveredItemRequest(APIBaseModel):
    order_item_id: UUID
    delivered_quantity: int = Field(ge=0)


class DeliveryConfirmRequest(APIBaseModel):
    recipient_name: str | None = Field(default=None, max_length=200)
    otp_code: str | None = Field(default=None, pattern=r"^[0-9]{4}$")
    proof_type: Literal["OTP_CODE", "PHYSICAL_SIGNATURE", "STORE_STAMP", "PHOTO_PROOF"] = "OTP_CODE"
    proof_media_id: UuidString | None = Field(default=None, max_length=64)
    issue_reported: str | None = Field(default=None, max_length=500)
    delivered_items: list[DeliveredItemRequest] | None = Field(default=None, max_length=500)


class MediaPresignRequest(APIBaseModel):
    mime_type: Literal["image/jpeg", "image/png", "image/webp"]
    file_size_bytes: int = Field(gt=0, le=5 * 1024 * 1024)
    target_type: Literal["PRODUCT", "VENDOR", "CANDIDATE", "DISPUTE", "DELIVERY", "PAYMENT", "SUPPORT"]
    target_id: UUID
    filename: str | None = Field(default=None, max_length=255)


class MediaResumableInitRequest(APIBaseModel):
    mime_type: Literal["image/jpeg", "image/png", "image/webp"]
    file_size_bytes: int = Field(gt=0, le=5 * 1024 * 1024)
    target_type: Literal["PRODUCT", "VENDOR", "CANDIDATE", "DISPUTE", "DELIVERY", "PAYMENT", "SUPPORT"]
    target_id: UUID
    filename: str | None = Field(default=None, max_length=255)

class MediaResumableCompletePart(APIBaseModel):
    part_number: int = Field(ge=1, le=10000)
    etag: str = Field(min_length=1, max_length=255)

class MediaResumableCompleteRequest(APIBaseModel):
    session_id: UUID
    parts: list[MediaResumableCompletePart] = Field(min_length=1, max_length=10000)

class MediaConfirmUploadRequest(APIBaseModel):
    media_id: UUID
    target_type: Literal["PRODUCT", "VENDOR", "CANDIDATE", "DISPUTE", "DELIVERY", "PAYMENT", "SUPPORT"]
    target_id: UUID


class DeliveryStageRequest(APIBaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class DeliveryExceptionReportRequest(APIBaseModel):
    delivery_id: UuidString = Field(min_length=1, max_length=64)
    order_id: UuidString = Field(min_length=1, max_length=64)
    exception_type: Literal[
        "DOORSTEP_REJECTION", "DAMAGED_GOODS", "ITEM_DISCREPANCY",
        "INCOMPLETE_DELIVERY", "VENDOR_NO_SHOW", "QUALITY_ISSUE", "OTHER",
    ]
    description: str | None = Field(default=None, max_length=2000)


class DeliveryExceptionResolveRequest(APIBaseModel):
    resolution_type: Literal[
        "FULL_REFUND", "PARTIAL_REFUND", "REPLACEMENT",
        "NO_ACTION", "RETURN_PICKUP", "ESCALATED_TO_OPS",
    ]
    resolution_note: str | None = Field(default=None, max_length=2000)


class DeliveryExceptionEscalateRequest(APIBaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class CategoryCreateRequest(APIBaseModel):
    name_fa: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    icon_url: str | None = Field(default=None, max_length=255)
    display_order: int = Field(default=0, ge=0)

class CategoryUpdateRequest(APIBaseModel):
    name_fa: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    icon_url: str | None = Field(default=None, max_length=255)
    display_order: int | None = Field(default=None, ge=0)

class BroadcastCreateRequest(APIBaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=20000)
    target_criteria: dict[str, object] = Field(min_length=1)
    channel: Literal["IN_APP", "SMS", "PUSH", "INBOX_AND_SMS", "ALL"] = "IN_APP"
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] = "NORMAL"
    scheduled_at: str | None = None

class BroadcastDispatchRequest(APIBaseModel):
    approve: bool = True

class NotificationPreferenceUpdateRequest(APIBaseModel):
    event_name: str = Field(min_length=1, max_length=100)
    channel: Literal["PUSH", "SMS"]
    is_enabled: bool


class FieldTaskCreateRequest(APIBaseModel):
    task_type: Literal[
        "ONBOARD_RETAILER", "TRAIN_RETAILER", "FIRST_ORDER_ASSIST",
        "FOLLOW_UP", "VENDOR_VISIT", "DISPUTE_VISIT",
    ]
    assigned_to_user_id: UuidString = Field(min_length=1, max_length=64)
    retailer_id: UuidString | None = Field(default=None, max_length=64)
    vendor_id: UuidString | None = Field(default=None, max_length=64)
    notes: str | None = Field(default=None, max_length=2000)


class FieldTaskUpdateRequest(APIBaseModel):
    status: Literal["ASSIGNED", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"] | None = None
    notes: str | None = Field(default=None, max_length=2000)


class ReturnItemRequest(APIBaseModel):
    order_item_id: UUID
    quantity: int = Field(gt=0)
    reason_code: Literal[
        "DAMAGED", "SHORTAGE", "WRONG_ITEM", "QUALITY", "DELIVERY_ERROR", "OTHER",
    ] = "OTHER"
    unit_refund_amount_toman: int | None = Field(default=None, ge=0)


class ReturnRequestRequest(APIBaseModel):
    items: list[ReturnItemRequest] = Field(min_length=1, max_length=MAX_BULK_ITEMS)
    reason: str = Field(min_length=1, max_length=1000)
    idempotency_key: str = Field(min_length=1, max_length=128)
    claimed_refund_amount_toman: int = Field(ge=0)


class ReturnTransitionRequest(APIBaseModel):
    target_status: str = Field(min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=1000)
    approved_refund_amount_toman: int | None = Field(default=None, ge=0)


class DisputeItemRequest(APIBaseModel):
    order_item_id: UUID
    quantity: int = Field(gt=0)
    claimed_amount_toman: int = Field(gt=0)
    reason_code: str = Field(min_length=1, max_length=50)


class DisputeOpenRequest(APIBaseModel):
    claimed_amount_toman: int = Field(gt=0)
    description: str = Field(min_length=1, max_length=2000)
    evidence_media_id: UUID
    items: list[DisputeItemRequest] = Field(min_length=1, max_length=MAX_BULK_ITEMS)


class PaymentEvidenceRequest(APIBaseModel):
    payment_id: UUID | None = None
    evidence_type: Literal[
        "BANK_REFERENCE", "POS_REFERENCE", "RECEIPT_IMAGE",
        "VENDOR_CONFIRMATION", "RETAILER_CONFIRMATION",
    ]
    reference_number: str = Field(min_length=1, max_length=255)
    amount_toman: int = Field(gt=0)
    evidence_media_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class PaymentVerifyRequest(APIBaseModel):
    notes: str | None = Field(default=None, max_length=2000)


class ReconciliationCaseResolveRequest(APIBaseModel):
    resolution_note: str | None = Field(default=None, max_length=2000)


class SupportCaseCreateRequest(APIBaseModel):
    case_type: Literal[
        "GENERAL", "ORDER_INQUIRY", "PAYMENT_ASSISTANCE", "DELIVERY_DELAY",
        "ACCOUNT_ISSUE", "CATALOG_SUGGESTION", "INVOICE_INQUIRY",
    ]
    subject: str = Field(min_length=1, max_length=500)
    related_order_id: UuidString | None = Field(default=None, max_length=64)
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] = "NORMAL"


class SupportCaseMessageRequest(APIBaseModel):
    message_text: str = Field(min_length=1, max_length=5000)


class ProductCandidateCreateRequest(APIBaseModel):
    proposed_title: str = Field(min_length=1, max_length=255)
    proposed_brand: str | None = Field(default=None, max_length=100)
    barcode: str | None = Field(default=None, max_length=100)
    vendor_sku: str | None = Field(default=None, max_length=100)
    photo_asset_id: UUID | None = None

class SupportCaseAssignRequest(APIBaseModel):
    assignee_user_id: UUID


class SupportCaseTransitionRequest(APIBaseModel):
    target_status: Literal["OPEN", "IN_PROGRESS", "WAITING_ON_USER", "RESOLVED", "CLOSED"]
    resolution_code: str | None = Field(default=None, max_length=50)
    resolution_note: str | None = Field(default=None, max_length=2000)


class ReferralCreateRequest(APIBaseModel):
    referral_code: str | None = Field(default=None, min_length=1, max_length=32)
    max_redemptions: int | None = Field(default=None, gt=0)
    expires_at: datetime | None = None


class ReferralRedeemRequest(APIBaseModel):
    pass



class VendorStaffInviteRequest(APIBaseModel):
    phone_number: str = Field(
        min_length=8,
        max_length=16,
        pattern=r"^\+[1-9][0-9]{7,14}$",
    )
    full_name: str = Field(min_length=1, max_length=100)


class VendorStaffUpdateRequest(APIBaseModel):
    role: Literal["VENDOR_OWNER", "VENDOR_STAFF"] | None = None
    status: Literal["INVITED", "ACTIVE", "SUSPENDED", "REVOKED"] | None = None


class AdminUserStatusRequest(APIBaseModel):
    is_active: bool

class DelegatedPermissionGrantRequest(APIBaseModel):
    permission_key: Literal[
        "catalog.view",
        "catalog.manage",
        "inventory.view",
        "inventory.scan",
        "inventory.adjust",
        "price.view",
        "price.manage",
        "order.view",
        "order.accept",
        "order.fulfillment",
        "delivery.dispatch",
        "delivery.handoff",
        "payment.view",
        "payment.record",
        "settlement.view",
        "membership.manage",
        "reports.view",
    ]
    reason: str = Field(min_length=1, max_length=500)
    client: str | None = Field(default=None, max_length=32)


class DelegatedPermissionRevokeRequest(APIBaseModel):
    reason: str = Field(min_length=1, max_length=500)
    client: str | None = Field(default=None, max_length=32)



class AdminOrganizationStatusRequest(APIBaseModel):
    status: Literal[
        "LEAD",
        "DOCUMENTS_PENDING",
        "UNDER_REVIEW",
        "VERIFICATION_PENDING",
        "APPROVED",
        "ACTIVE",
        "REJECTED",
        "SUSPENDED",
    ]


class AdminSlaOverrideRequest(APIBaseModel):
    order_id: UUID
    extension_minutes: int = Field(ge=1, le=1440)
    reason: str = Field(min_length=1, max_length=500)


class AdminBroadcastCreateRequest(APIBaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=5000)
    target_criteria: dict = Field(default_factory=dict)
    channel: Literal["IN_APP", "SMS", "PUSH", "INBOX_AND_SMS", "ALL"] = "IN_APP"
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] = "NORMAL"
    scheduled_at: datetime | None = None


class AdminBroadcastDispatchRequest(APIBaseModel):
    approve: bool = True


class AdminCategoryCreateRequest(APIBaseModel):
    name_fa: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    icon_url: str | None = Field(default=None, max_length=255)
    display_order: int = Field(default=0, ge=0)


class AdminCategoryUpdateRequest(APIBaseModel):
    name_fa: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    icon_url: str | None = Field(default=None, max_length=255)
    display_order: int | None = Field(default=None, ge=0)


class VendorInventoryContinuousScanRequest(APIBaseModel):
    product_id: UUID
    vendor_sku: str = Field(min_length=1, max_length=100)
    packaging_unit: str = Field(min_length=1, max_length=30)
    pack_quantity: int = Field(ge=1, le=100000)
    physical_quantity: int = Field(ge=0)
    unit_price_toman: int = Field(gt=0)
    consumer_price_per_unit_toman: int | None = Field(default=None, gt=0)
    session_id: str = Field(min_length=1, max_length=128)


class VendorInventoryPublishRequest(APIBaseModel):
    session_id: str = Field(min_length=1, max_length=128)


class DisputeTransitionReasonRequest(APIBaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class DisputeResolveRequest(APIBaseModel):
    outcome: Literal[
        "ADJUSTED_SHORTAGE",
        "REPLACEMENT_ORDER",
        "REJECTED_CLAIM",
        "MUTUAL_AGREEMENT",
    ]
    approved_amount_toman: int = Field(ge=0)
    reason: str = Field(min_length=1, max_length=1000)


class RefundIssueRequest(APIBaseModel):
    dispute_id: UUID
    amount_toman: int = Field(gt=0)
    payment_id: UUID | None = None
    reason: str = Field(min_length=1, max_length=1000)


class RefundApproveRequest(APIBaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class RefundCompleteRequest(APIBaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class BarcodeMatchRequest(APIBaseModel):
    # Legacy contract shape (raw_barcode + scan_source) remains accepted.
    raw_barcode: str | None = Field(default=None, min_length=8, max_length=32)
    scan_source: str | None = Field(default=None, min_length=1, max_length=50)
    # Extended remediation shape adds optional candidate creation inputs.
    barcode: str | None = Field(default=None, min_length=8, max_length=32)
    proposed_title: str | None = Field(default=None, max_length=255)
    vendor_sku: str | None = Field(default=None, max_length=100)
    packaging_unit: str = Field(default="UNIT", min_length=1, max_length=30)
    pack_quantity: int = Field(default=1, ge=1, le=100000)
    create_candidate: bool = False


class AdminProductCandidateReviewRequest(APIBaseModel):
    action: Literal["APPROVE_CANONICAL", "MERGE_EXISTING", "REJECT"]
    reason: str = Field(min_length=1, max_length=1000)
    brand_id: UUID | None = None
    category_id: UUID | None = None
    subcategory_id: UUID | None = None
    canonical_name_fa: str | None = Field(default=None, max_length=255)
    target_product_id: UUID | None = None
