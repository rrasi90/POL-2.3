"""Vendor inventory continuous-scan and publish routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    VendorInventoryContinuousScanRequest,
    VendorInventoryPublishRequest,
)

router = APIRouter(prefix="/vendors/inventory", tags=["inventory"])


@router.post("/continuous-scan")
def continuous_scan(
    payload: VendorInventoryContinuousScanRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_inventory_continuous_scan(
            product_id=str(payload.product_id),
            vendor_sku=payload.vendor_sku,
            packaging_unit=payload.packaging_unit,
            pack_quantity=payload.pack_quantity,
            physical_quantity=payload.physical_quantity,
            unit_price_toman=payload.unit_price_toman,
            consumer_price_per_unit_toman=payload.consumer_price_per_unit_toman,
            session_id=payload.session_id,
        )
    )


@router.post("/publish")
def publish_inventory(
    payload: VendorInventoryPublishRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.vendor_inventory_publish(session_id=payload.session_id)
    )
