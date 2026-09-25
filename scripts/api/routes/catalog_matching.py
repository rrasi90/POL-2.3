"""Catalog barcode lookup and matching routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary, require_roles
from scripts.api.errors import success_payload
from scripts.api.schemas import BarcodeMatchRequest

router = APIRouter(tags=["catalog-matching"])


@router.get("/catalog/barcode/lookup")
def barcode_lookup(
    barcode: str = Query(min_length=8, max_length=32),
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.catalog_barcode_match(
            barcode=barcode,
            create_candidate=False,
        )
    )


@router.post("/products/match-barcode")
def match_barcode(
    payload: BarcodeMatchRequest,
    boundary=Depends(get_application_boundary),
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF"))] = None,
):
    return success_payload(
        boundary.catalog_barcode_match(
            barcode=payload.barcode,
            proposed_title=payload.proposed_title,
            vendor_sku=payload.vendor_sku,
            packaging_unit=payload.packaging_unit,
            pack_quantity=payload.pack_quantity,
            create_candidate=payload.create_candidate,
        )
    )
