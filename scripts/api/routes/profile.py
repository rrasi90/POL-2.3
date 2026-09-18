"""Authenticated profile routes backed exclusively by POLApplicationBoundary."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import MembershipProfileUpdateRequest, ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["profile"])
membership_router = APIRouter(prefix="/membership", tags=["profile"])


@router.get("")
def get_profile(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.profile_get())


@router.get("/completion")
def get_profile_completion(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.profile_completion())


@router.get("/context")
def get_profile_context(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.profile_get())


@router.put("")
def update_profile(
    payload: ProfileUpdateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.profile_update(fields=payload.model_dump(exclude_unset=True))
    )


@membership_router.get("/profile")
def get_membership_profile(boundary=Depends(get_application_boundary)):
    profile = boundary.profile_get()
    return success_payload(profile["membership_profile"])


@membership_router.put("/profile")
def update_membership_profile(
    payload: MembershipProfileUpdateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.profile_membership_update(
            fields=payload.model_dump(exclude_unset=True)
        )
    )
