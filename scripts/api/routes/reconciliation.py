"""Authenticated reconciliation exception management HTTP routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import ReconciliationCaseResolveRequest


router = APIRouter(prefix="/finance/reconciliation", tags=["reconciliation"])


@router.get("")
def list_reconciliation_cases(
    case_status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.reconciliation_cases_list(
            status=case_status, offset=offset, limit=limit,
        )
    )


@router.get("/{case_id}")
def get_reconciliation_case(
    case_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.reconciliation_case_get(case_id=str(case_id))
    )


@router.patch("/{case_id}/resolve")
def resolve_reconciliation_case(
    case_id: UUID,
    payload: ReconciliationCaseResolveRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.reconciliation_case_resolve(
            case_id=str(case_id),
            resolution_note=payload.resolution_note,
        )
    )
