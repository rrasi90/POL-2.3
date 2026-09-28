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
    _auth: Annotated[dict, Depends(require_roles("VENDOR_OWNER", "VENDOR_STAFF", "FIELD_ACTIVATOR"))] = None,
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
    barcode = payload.barcode or payload.raw_barcode
    if not barcode:
        raise ValueError("barcode or raw_barcode is required.")

    result = boundary.catalog_barcode_match(
        barcode=barcode,
        proposed_title=payload.proposed_title,
        vendor_sku=payload.vendor_sku,
        packaging_unit=payload.packaging_unit,
        pack_quantity=payload.pack_quantity,
        create_candidate=payload.create_candidate,
    )
    # Preserve the canonical legacy response key while exposing the current richer shape.
    result.setdefault("match_status", result.get("match_type"))
    if payload.scan_source:
        result["scan_source"] = payload.scan_source
    return success_payload(result)
