"""Public vendor storefront routes — no authentication required."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from scripts.api.db import get_db_cursor
from scripts.api.errors import success_payload

router = APIRouter(prefix="/storefront", tags=["storefront"])


def _boundary(cur=Depends(get_db_cursor)):
    from scripts.application_boundary import POLApplicationBoundary

    return POLApplicationBoundary(cur, context=None)


@router.get("/vendors")
def storefront_list_vendors(
    q: str | None = Query(default=None, max_length=200),
    category_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    cur=Depends(get_db_cursor),
):
    """List all active vendors with optional search and category filtering."""
    from scripts.application_boundary import POLApplicationBoundary

    boundary = POLApplicationBoundary(cur, context=None)
    offset = (page - 1) * page_size
    results = boundary.storefront_list_vendors(
        query=q,
        category_id=str(category_id) if category_id else None,
        limit=page_size,
        offset=offset,
    )
    return success_payload({
        "items": results.get("items", []),
        "total": results.get("total", 0),
        "page": page,
        "page_size": page_size,
    })


@router.get("/vendors/{vendor_id}")
def storefront_vendor_detail(
    vendor_id: UUID,
    cur=Depends(get_db_cursor),
):
    """Get public vendor detail including info, products, and ratings."""
    from scripts.application_boundary import POLApplicationBoundary

    boundary = POLApplicationBoundary(cur, context=None)
    return success_payload(boundary.storefront_vendor_detail(str(vendor_id)))


@router.get("/vendors/{vendor_id}/products")
def storefront_vendor_products(
    vendor_id: UUID,
    category_id: UUID | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    sort: str = Query(default="name", pattern="^(name|price|newest)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    cur=Depends(get_db_cursor),
):
    """List products for a vendor with optional filtering, search, and sorting."""
    from scripts.application_boundary import POLApplicationBoundary

    boundary = POLApplicationBoundary(cur, context=None)
    offset = (page - 1) * page_size
    results = boundary.storefront_vendor_products(
        vendor_id=str(vendor_id),
        category_id=str(category_id) if category_id else None,
        query=q,
        sort=sort,
        limit=page_size,
        offset=offset,
    )
    return success_payload({
        "items": results.get("items", []),
        "total": results.get("total", 0),
        "page": page,
        "page_size": page_size,
    })
