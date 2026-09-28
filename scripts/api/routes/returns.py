"""Authenticated return/RMA HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import ReturnRequestRequest, ReturnTransitionRequest


router = APIRouter(prefix="/orders", tags=["returns"])
returns_router = APIRouter(prefix="/returns", tags=["returns"])


def _validate_idempotency_key(value: str) -> str:
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError("Idempotency-Key must be a valid UUIDv4.") from exc
    if parsed.version != 4:
        raise ValueError("Idempotency-Key must be a UUIDv4.")
    return str(parsed)


@router.post("/{order_id}/returns", status_code=status.HTTP_201_CREATED)
def create_return_request(
    order_id: UUID,
    payload: ReturnRequestRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=1, max_length=128),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.return_request(
            order_id=str(order_id),
            order_items=[
                {
                    "order_item_id": str(item.order_item_id),
                    "quantity": item.quantity,
                    "reason_code": item.reason_code,
                    "unit_refund_amount_toman": item.unit_refund_amount_toman,
                }
                for item in payload.items
            ],
            reason=payload.reason,
            idempotency_key=_validate_idempotency_key(idempotency_key),
            claimed_refund_amount_toman=payload.claimed_refund_amount_toman,
        )
    )


@router.get("/{order_id}/returns")
def list_returns_for_order(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.returns_list(order_id=str(order_id))
    )


@returns_router.get("/{return_id}")
def get_return(
    return_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.return_get(return_id=str(return_id))
    )


@returns_router.post("/{return_id}/refund/approve")
def approve_return_refund(
    return_id: UUID,
    payload: ReturnTransitionRequest,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(
        boundary.return_refund_approve(
            return_id=str(return_id),
            reason=payload.reason,
        )
    )


@returns_router.patch("/{return_id}")
def transition_return(
    return_id: UUID,
    payload: ReturnTransitionRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.return_transition(
            return_id=str(return_id),
            target_status=payload.target_status,
            reason=payload.reason,
            approved_refund_amount_toman=payload.approved_refund_amount_toman,
        )
    )
