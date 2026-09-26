"""Authenticated vendor catalog, pricing, and inventory management routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary, require_permission
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    VendorCatalogCreateRequest,
    VendorCatalogUpdateRequest,
    VendorInventoryAdjustRequest,
    VendorPriceSetRequest,
)

router = APIRouter(prefix="/catalog/vendors", tags=["catalog"])


@router.get("/products")
def vendor_list_products(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.vendor_catalog_list_products())


@router.post("/products")
def vendor_create_product(
    payload: VendorCatalogCreateRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_permission("catalog.manage"))] = None,
):
    return success_payload(
        boundary.vendor_catalog_create_product(
            vendor_sku=payload.vendor_sku,
            product_id=str(payload.product_id) if payload.product_id else None,
            candidate_id=str(payload.candidate_id) if payload.candidate_id else None,
            packaging_unit=payload.packaging_unit,
            pack_quantity=payload.pack_quantity,
            sales_unit=payload.sales_unit,
            initial_price_toman=payload.initial_price_toman,
            moq=payload.moq,
        )
    )


@router.patch("/products/{vendor_product_id}")
def vendor_update_product(
    vendor_product_id: UUID,
    payload: VendorCatalogUpdateRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_permission("catalog.manage"))] = None,
):
    return success_payload(
        boundary.vendor_catalog_update_product(
            vendor_product_id=str(vendor_product_id),
            packaging_unit=payload.packaging_unit,
            pack_quantity=payload.pack_quantity,
            sales_unit=payload.sales_unit,
            moq=payload.moq,
            is_active=payload.is_active,
        )
    )


@router.get("/products/{vendor_product_id}/prices")
def vendor_price_history(
    vendor_product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.vendor_price_history(str(vendor_product_id)))


@router.get("/products/{vendor_product_id}/prices/current")
def vendor_price_current(
    vendor_product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.vendor_price_current(str(vendor_product_id)))


@router.post("/products/{vendor_product_id}/prices")
def vendor_price_set(
    vendor_product_id: UUID,
    payload: VendorPriceSetRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_permission("price.manage"))] = None,
):
    return success_payload(
        boundary.vendor_price_set(
            vendor_product_id=str(vendor_product_id),
            price_toman=payload.price_toman,
        )
    )


@router.get("/products/{vendor_product_id}/inventory")
def vendor_inventory_get(
    vendor_product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.vendor_inventory_get(str(vendor_product_id)))


@router.patch("/products/{vendor_product_id}/inventory")
def vendor_inventory_adjust(
    vendor_product_id: UUID,
    payload: VendorInventoryAdjustRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_permission("inventory.adjust"))] = None,
):
    return success_payload(
        boundary.vendor_inventory_adjust(
            vendor_product_id=str(vendor_product_id),
            new_physical_quantity=payload.new_physical_quantity,
            reason=payload.reason,
        )
    )
