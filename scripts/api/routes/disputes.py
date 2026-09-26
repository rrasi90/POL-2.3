"""Authenticated dispute HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import DisputeOpenRequest, DisputeResolveRequest


router = APIRouter(prefix="/orders", tags=["disputes"])
disputes_router = APIRouter(prefix="/disputes", tags=["disputes"])


@router.post("/{order_id}/disputes", status_code=status.HTTP_201_CREATED)
def open_dispute(
    order_id: UUID,
    payload: DisputeOpenRequest,
    idempotency_key: str = Header(default=None, alias="Idempotency-Key"),
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("RETAILER_OWNER")),
):
    return success_payload(
        boundary.dispute_open(
            order_id=str(order_id),
            claimed_amount_toman=payload.claimed_amount_toman,
            description=payload.description,
            evidence_media_id=str(payload.evidence_media_id),
            items=payload.items,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/{order_id}/disputes")
def list_disputes_for_order(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.disputes_list(order_id=str(order_id))
    )


@disputes_router.post("/{dispute_id}/investigate")
def investigate_dispute(
    dispute_id: UUID,
    payload: DisputeResolveRequest,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(
        boundary.dispute_investigate(dispute_id=str(dispute_id), reason=payload.reason)
    )


@disputes_router.get("/{dispute_id}")
def get_dispute(
    dispute_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.dispute_get(dispute_id=str(dispute_id))
    )



@disputes_router.patch("/{dispute_id}/resolve")
def resolve_dispute(
    dispute_id: UUID,
    payload: DisputeResolveRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.dispute_resolve(
            dispute_id=str(dispute_id),
            outcome=payload.outcome,
            approved_amount_toman=payload.approved_amount_toman,
            reason=payload.reason,
        )
    )



@disputes_router.post("/{dispute_id}/close")
def close_dispute(
    dispute_id: UUID,
    payload: DisputeResolveRequest,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(
        boundary.dispute_close(dispute_id=str(dispute_id), reason=payload.reason)
    )
