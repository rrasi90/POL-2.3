"""Catalog identifier and candidate contract routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import ProductCandidateCreateRequest

candidates_router = APIRouter(prefix="/product-candidates", tags=["catalog-candidates"])

@candidates_router.post("", status_code=status.HTTP_201_CREATED)
def create_product_candidate(
    payload: ProductCandidateCreateRequest,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF")),
):
    return success_payload(
        boundary.catalog_create_product_candidate(
            proposed_title=payload.proposed_title,
            proposed_brand=payload.proposed_brand,
            barcode=payload.barcode,
            vendor_sku=payload.vendor_sku,
            photo_asset_id=str(payload.photo_asset_id) if payload.photo_asset_id else None,
        )
    )