"""Public unified search routes — no authentication required."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from scripts.api.db import get_db_cursor
from scripts.api.errors import success_payload

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def unified_search(
    q: str = Query(min_length=1, max_length=200),
    type: str | None = Query(default=None, pattern="^(product|vendor|category)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    cur=Depends(get_db_cursor),
):
    """Search across products, vendors, and categories in a single request.

    Returns results grouped by type. Use the ``type`` parameter to restrict
    the search to a single entity kind.
    """
    from scripts.application_boundary import POLApplicationBoundary

    boundary = POLApplicationBoundary(cur, context=None)
    offset = (page - 1) * page_size
    results = boundary.unified_search(
        query=q,
        result_type=type,
        limit=page_size,
        offset=offset,
    )
    return success_payload({
        "query": q,
        "products": results.get("products", []),
        "vendors": results.get("vendors", []),
        "categories": results.get("categories", []),
        "page": page,
        "page_size": page_size,
    })
