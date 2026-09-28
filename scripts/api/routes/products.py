"""Public contract-compatible catalog search route."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from scripts.api.db import get_db_cursor
from scripts.api.errors import success_payload
from scripts.application_boundary import ApplicationContext, POLApplicationBoundary

router = APIRouter(prefix="/products", tags=["catalog-public"])

@router.get("/search")
def products_search(
    q: str = Query(min_length=1, max_length=200),
    category_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    cur=Depends(get_db_cursor),
):
    boundary = POLApplicationBoundary(
        cur, ApplicationContext(user_id="", organization_id=None, correlation_id="public-catalog-search")
    )
    return success_payload(
        boundary.catalog_products_search(
            query=q,
            category_id=str(category_id) if category_id else None,
            page=page,
            limit=limit,
        )
    )