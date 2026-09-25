"""Canonical public category route."""

from fastapi import APIRouter, Depends

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload

router = APIRouter(prefix="/categories", tags=["catalog-public"])


@router.get("")
def categories_list(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.catalog_categories_public())
