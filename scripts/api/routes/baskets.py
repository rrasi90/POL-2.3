"""Authenticated basket and allocation HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import BasketItemRequest

router = APIRouter(prefix="/baskets", tags=["baskets"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_basket(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.basket_create())


@router.get("/current", status_code=status.HTTP_200_OK)
def current_basket(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.basket_current())

@router.post("/{basket_id}/items", status_code=status.HTTP_200_OK)
def add_basket_item(
    basket_id: UUID,
    payload: BasketItemRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.basket_add_item(
            basket_id=str(basket_id),
            product_id=str(payload.product_id),
            quantity=payload.requested_quantity,
            pack_quantity=payload.pack_quantity,
            expected_version=payload.expected_version,
        )
    )


@router.post("/{basket_id}/allocation-preview", status_code=status.HTTP_200_OK)
def allocation_preview(
    basket_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.basket_allocation_preview(basket_id=str(basket_id))
    )
