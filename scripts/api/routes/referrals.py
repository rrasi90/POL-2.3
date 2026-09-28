"""Vendor referral HTTP routes — create, list, get, redeem."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import ReferralCreateRequest, ReferralRedeemRequest


router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_referral(
    payload: ReferralCreateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.referral_create(
            referral_code=payload.referral_code,
            max_redemptions=payload.max_redemptions,
            expires_at=payload.expires_at,
        )
    )


@router.get("")
def list_referrals(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.referral_list(offset=offset, limit=limit)
    )


@router.get("/{referral_id}")
def get_referral(
    referral_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.referral_get(referral_id=str(referral_id))
    )


@router.post("/{referral_id}/redeem")
def redeem_referral(
    referral_id: UUID,
    payload: ReferralRedeemRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.referral_redeem(referral_id=str(referral_id))
    )
