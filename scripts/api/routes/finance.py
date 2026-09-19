"""Authenticated finance (invoice / settlement) HTTP routes — read-only."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload


invoices_router = APIRouter(prefix="/invoices", tags=["finance"])
settlements_router = APIRouter(prefix="/vendors/settlements", tags=["finance"])
settlement_detail_router = APIRouter(prefix="/settlements", tags=["finance"])
order_invoice_router = APIRouter(prefix="/orders", tags=["finance"])


@invoices_router.get("")
def list_invoices(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.invoices_list(offset=offset, limit=limit)
    )


@invoices_router.get("/{invoice_id}")
def get_invoice(
    invoice_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.invoice_get(invoice_id=str(invoice_id))
    )


@order_invoice_router.get("/{order_id}/invoice")
def get_invoice_for_order(
    order_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.invoice_by_order(order_id=str(order_id))
    )


@settlements_router.get("")
def list_settlements(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.settlements_list(offset=offset, limit=limit)
    )


@settlement_detail_router.get("/{settlement_id}")
def get_settlement(
    settlement_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.settlement_get(settlement_id=str(settlement_id))
    )
