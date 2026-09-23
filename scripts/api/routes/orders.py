"""Authenticated order HTTP routes — writes (checkout/accept/reject) + reads (query/timeline)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    CheckoutRequest,
    DeliveryConfirmRequest,
    DeliveryExceptionEscalateRequest,
    DeliveryExceptionReportRequest,
    DeliveryExceptionResolveRequest,
    DispatchRequest,
    PaymentEvidenceRequest,
    PaymentVerifyRequest,
    RetailerPartialAcceptanceDeclineRequest,
    VendorOrderRejectRequest,
    VendorPartialAcceptanceProposalRequest,
)


router = APIRouter(prefix="/orders", tags=["orders"])


def _validate_idempotency_key(value: str) -> str:
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError("Idempotency-Key must be a valid UUIDv4.") from exc
    if parsed.version != 4:
        raise ValueError("Idempotency-Key must be a UUIDv4.")
    return str(parsed)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CheckoutRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=128),
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("RETAILER_OWNER", "RETAILER_STAFF"))] = None,
):
    return success_payload(
        boundary.checkout_from_allocation_plan(
            allocation_plan_id=str(payload.allocation_plan_id),
            delivery_address=payload.delivery_address,
            preferred_payment_method=payload.preferred_payment_method,
            idempotency_key=_validate_idempotency_key(idempotency_key),
        )
    )


@router.post("/{order_id}/accept", status_code=200)
def accept_order(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_order_accept(order_id=str(order_id))
    )


@router.post("/{order_id}/reject", status_code=200)
def reject_order(
    order_id: UUID,
    payload: VendorOrderRejectRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_order_reject(
            order_id=str(order_id),
            rejection_reason=payload.reason,
        )
    )

 
 
@router.post("/{order_id}/partial-acceptance-proposals", status_code=201)
def propose_partial_acceptance(
    order_id: UUID,
    payload: VendorPartialAcceptanceProposalRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=128),
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_partial_acceptance_propose(
            order_id=str(order_id),
            idempotency_key=_validate_idempotency_key(idempotency_key),
            items=[
                {
                    "order_item_id": str(item.order_item_id),
                    "accepted_quantity": item.accepted_quantity,
                    "reason": item.reason,
                }
                for item in payload.items
            ],
        )
    )


@router.post("/{order_id}/partial-acceptance-proposals/{proposal_id}/approve", status_code=200)
def approve_partial_acceptance(
    order_id: UUID,
    proposal_id: UUID,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("RETAILER_OWNER", "RETAILER_STAFF"))] = None,
):
    return success_payload(
        boundary.retailer_partial_acceptance_approve(
            order_id=str(order_id),
            proposal_id=str(proposal_id),
        )
    )


@router.post("/{order_id}/partial-acceptance-proposals/{proposal_id}/decline", status_code=200)
def decline_partial_acceptance(
    order_id: UUID,
    proposal_id: UUID,
    payload: RetailerPartialAcceptanceDeclineRequest | None = None,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("RETAILER_OWNER", "RETAILER_STAFF"))] = None,
):
    return success_payload(
        boundary.retailer_partial_acceptance_decline(
            order_id=str(order_id),
            proposal_id=str(proposal_id),
            reason=payload.reason if payload else None,
        )
    )


# ── Order Query Routes (Stage 20) ─────────────────────────────────


@router.get("")
def list_orders(
    order_status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.order_list(status=order_status, offset=offset, limit=limit)
    )


@router.get("/{order_id}")
def get_order(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.order_get(order_id=str(order_id))
    )


@router.get("/{order_id}/items")
def get_order_items(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.order_items_list(order_id=str(order_id))
    )


@router.get("/{order_id}/timeline")
def get_order_timeline(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.order_timeline(order_id=str(order_id))
    )


@router.get("/group/{order_group_id}")
def get_order_group(
    order_group_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.order_group_get(order_group_id=str(order_group_id))
    )


@router.get("/group/{order_group_id}/orders")
def get_order_group_child_orders(
    order_group_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.order_group_child_orders(order_group_id=str(order_group_id))
    )


# ── Fulfillment Routes (Stage 22) ─────────────────────────────────


@router.post("/{order_id}/preparing", status_code=200)
def mark_preparing(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_mark_preparing(order_id=str(order_id))
    )


@router.post("/{order_id}/ready", status_code=200)
def mark_ready(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_mark_ready(order_id=str(order_id))
    )


@router.post("/{order_id}/dispatch", status_code=200)
def dispatch_order(
    order_id: UUID,
    payload: DispatchRequest | None = None,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    kwargs = {"order_id": str(order_id)}
    if payload:
        if payload.driver_name:
            kwargs["driver_name"] = payload.driver_name
        if payload.vehicle_plate:
            kwargs["vehicle_plate"] = payload.vehicle_plate
        if payload.driver_phone:
            kwargs["driver_phone"] = payload.driver_phone
    return success_payload(boundary.vendor_dispatch_order(**kwargs))


@router.post("/{order_id}/deliver", status_code=200)
def confirm_delivery(
    order_id: UUID,
    payload: DeliveryConfirmRequest | None = None,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("RETAILER_OWNER", "RETAILER_STAFF", "FIELD_ACTIVATOR"))] = None,
):
    kwargs = {"order_id": str(order_id)}
    if payload:
        if payload.recipient_name:
            kwargs["recipient_name"] = payload.recipient_name
        if payload.otp_code:
            kwargs["otp_code"] = payload.otp_code
        if payload.proof_type:
            kwargs["proof_type"] = payload.proof_type
        if payload.proof_media_id:
            kwargs["proof_media_id"] = payload.proof_media_id
        if payload.issue_reported:
            kwargs["issue_reported"] = payload.issue_reported
    return success_payload(boundary.retailer_confirm_delivery(**kwargs))


# ── Delivery Tracking Routes (Stage 23) ────────────────────────────


@router.get("/{order_id}/delivery")
def get_delivery(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delivery_get(order_id=str(order_id))
    )


@router.get("/{order_id}/delivery/proof")
def get_delivery_proof(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    proof = boundary.delivery_proof(order_id=str(order_id))
    return success_payload(proof if proof else {"message": "No proof of delivery found."})


# ── Delivery Exception Routes (Stage 25) ──────────────────────────


@router.post("/{order_id}/delivery-exceptions", status_code=201)
def report_delivery_exception(
    order_id: UUID,
    payload: DeliveryExceptionReportRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.report_delivery_exception(
            delivery_id=payload.delivery_id,
            order_id=str(order_id),
            exception_type=payload.exception_type,
            description=payload.description,
        )
    )


@router.get("/{order_id}/delivery-exceptions")
def list_delivery_exceptions(
    order_id: UUID,
    status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delivery_exceptions_list(
            order_id=str(order_id),
            status=status,
            offset=offset,
            limit=limit,
        )
    )


@router.get("/delivery-exceptions/{exception_id}")
def get_delivery_exception(
    exception_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.delivery_exception_get(exception_id=str(exception_id))
    )


@router.patch("/delivery-exceptions/{exception_id}/resolve")
def resolve_delivery_exception(
    exception_id: UUID,
    payload: DeliveryExceptionResolveRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("OPS_AGENT", "VENDOR_OWNER"))] = None,
):
    return success_payload(
        boundary.resolve_delivery_exception(
            exception_id=str(exception_id),
            resolution_type=payload.resolution_type,
            resolution_note=payload.resolution_note,
        )
    )


@router.patch("/delivery-exceptions/{exception_id}/escalate")
def escalate_delivery_exception(
    exception_id: UUID,
    payload: DeliveryExceptionEscalateRequest | None = None,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.escalate_delivery_exception(
            exception_id=str(exception_id),
            reason=payload.reason if payload else None,
        )
    )


# ── Payment Evidence Routes (Stage 27) ────────────────────────────


@router.post("/{order_id}/payments/evidence", status_code=201)
def submit_payment_evidence(
    order_id: UUID,
    payload: PaymentEvidenceRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.submit_payment_evidence(
            order_id=str(order_id),
            evidence_type=payload.evidence_type,
            reference_number=payload.reference_number,
            amount_toman=payload.amount_toman,
            notes=payload.notes,
        )
    )


@router.get("/{order_id}/payments/evidence")
def list_payment_evidence(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.get_payment_evidence(order_id=str(order_id))
    )


@router.post("/{order_id}/payments/verify", status_code=200)
def verify_payment(
    order_id: UUID,
    payload: PaymentVerifyRequest | None = None,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("OPS_AGENT", "VENDOR_OWNER"))] = None,
):
    return success_payload(
        boundary.verify_payment(
            order_id=str(order_id),
            notes=payload.notes if payload else None,
        )
    )
