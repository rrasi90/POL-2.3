"""Authenticated order checkout HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import CheckoutRequest


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
):
    return success_payload(
        boundary.vendor_order_accept(order_id=str(order_id))
    )
