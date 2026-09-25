"""Authenticated dispute HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import DisputeOpenRequest


router = APIRouter(prefix="/orders", tags=["disputes"])
disputes_router = APIRouter(prefix="/disputes", tags=["disputes"])


@router.post("/{order_id}/disputes", status_code=status.HTTP_201_CREATED)
def open_dispute(
    order_id: UUID,
    payload: DisputeOpenRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.dispute_open(
            order_id=str(order_id),
            claimed_amount_toman=payload.claimed_amount_toman,
            description=payload.description,
            evidence_media_id=str(payload.evidence_media_id) if payload.evidence_media_id else None,
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


@disputes_router.get("/{dispute_id}")
def get_dispute(
    dispute_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.dispute_get(dispute_id=str(dispute_id))
    )
