"""Authenticated catalog read routes backed exclusively by POLApplicationBoundary."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/search")
def catalog_search(
    q: str = Query(min_length=1, max_length=200),
    category_id: UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    boundary=Depends(get_application_boundary),
):
    results = boundary.catalog_search(
        query=q,
        category_id=str(category_id) if category_id else None,
        limit=limit,
    )
    return success_payload({"items": results, "query": q})


@router.get("/categories")
def catalog_categories(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.catalog_categories_public())


@router.get("/products/{product_id}")
def catalog_product_detail(
    product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.catalog_product_detail(str(product_id)))


@router.get("/products/{product_id}/vendors")
def catalog_product_vendors(
    product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.catalog_product_vendors(str(product_id)))


@router.get("/products/{product_id}/compare-prices")
def catalog_compare_prices(
    product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.catalog_compare_prices(str(product_id)))


@router.get("/products/{product_id}/compare-inventory")
def catalog_compare_inventory(
    product_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.catalog_inventory_compare(str(product_id)))
