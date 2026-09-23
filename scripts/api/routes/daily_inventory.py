"""Authenticated daily inventory confirmation routes — Stage 18."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    DailyInventoryConfirmRequest,
    DailyInventoryConfirmWithChangesRequest,
)

router = APIRouter(prefix="/inventory/daily", tags=["inventory"])


@router.get("/{confirmation_date}")
def daily_inventory_get(
    confirmation_date: str,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.daily_inventory_get(confirmation_date))


@router.post("/{confirmation_date}/confirm")
def daily_inventory_confirm_no_changes(
    confirmation_date: str,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.daily_inventory_confirm_no_changes(confirmation_date))


@router.post("/{confirmation_date}/confirm-with-changes")
def daily_inventory_confirm_with_changes(
    confirmation_date: str,
    payload: DailyInventoryConfirmWithChangesRequest,
    boundary=Depends(get_application_boundary),
):
    changes = [
        {"vendor_product_id": str(c.vendor_product_id), "declared_quantity": c.declared_quantity}
        for c in payload.changes
    ]
    return success_payload(boundary.daily_inventory_confirm_with_changes(confirmation_date, changes))
