"""Canonical public category route."""

from fastapi import APIRouter, Depends

from scripts.api.db import get_db_cursor
from scripts.api.errors import success_payload
from scripts.application_boundary import POLApplicationBoundary

router = APIRouter(prefix="/categories", tags=["catalog-public"])


@router.get("")
def categories_list(cur=Depends(get_db_cursor)):
    """Return the public category tree without requiring an authenticated session."""
    boundary = POLApplicationBoundary(cur, context=None)
    return success_payload(boundary.catalog_categories_public())
