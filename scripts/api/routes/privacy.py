"""Authenticated privacy lifecycle routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import PrivacyExportRequest

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.post("/export")
def request_data_export(
    payload: PrivacyExportRequest | None = None,
    boundary=Depends(get_application_boundary),
):
    # The current export contract is a complete authenticated personal-data
    # snapshot. include_activity_counts is accepted for forward compatibility.
    _ = payload
    return success_payload(boundary.privacy_export())


@router.post("/deletion")
def request_account_deletion(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.privacy_delete_account())
