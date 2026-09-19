"""Authenticated vendor catalog management routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import (
    VendorCatalogCreateRequest,
    VendorCatalogUpdateRequest,
)

router = APIRouter(prefix="/catalog/vendors", tags=["catalog"])


@router.get("/products")
def vendor_list_products(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.vendor_catalog_list_products())


@router.post("/products")
def vendor_create_product(
    payload: VendorCatalogCreateRequest,
    boundary=Depends(get_application_boundary),
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
