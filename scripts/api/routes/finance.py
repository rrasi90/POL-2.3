"""Authenticated finance (invoice / settlement) HTTP routes — read-only."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import RefundApproveRequest, RefundCompleteRequest, RefundIssueRequest


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



refunds_router = APIRouter(prefix="/finance/refunds", tags=["finance"])


@refunds_router.post("/issue")
def issue_refund(
    payload: RefundIssueRequest,
    idempotency_key: str = Header(default=None, alias="Idempotency-Key"),
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(
        boundary.refund_issue(
            dispute_id=str(payload.dispute_id),
            amount_toman=payload.amount_toman,
            payment_id=str(payload.payment_id) if payload.payment_id else None,
            reason=payload.reason,
            idempotency_key=idempotency_key,
        )
    )


@refunds_router.get("")
def list_refunds(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(boundary.refunds_list(offset=offset, limit=limit))


@refunds_router.get("/{refund_id}")
def get_refund(
    refund_id: UUID,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(boundary.refund_get(refund_id=str(refund_id)))


@refunds_router.post("/{refund_id}/approve")
def approve_refund(
    refund_id: UUID,
    payload: RefundApproveRequest,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(boundary.refund_approve(refund_id=str(refund_id), reason=payload.reason))


@refunds_router.post("/{refund_id}/complete")
def complete_refund(
    refund_id: UUID,
    payload: RefundCompleteRequest,
    boundary=Depends(get_application_boundary),
    _auth=Depends(require_roles("OPS_AGENT","OPS_ADMIN","ADMIN_SUPER","SUPER_ADMIN")),
):
    return success_payload(boundary.refund_complete(refund_id=str(refund_id), reason=payload.reason))
