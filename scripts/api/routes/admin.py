"""Admin-only HTTP routes — audit logs and exception dashboard."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit-logs")
def list_audit_logs(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_audit_logs_list(offset=offset, limit=limit)
    )


@router.get("/exceptions/dashboard")
def exceptions_dashboard(
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_exceptions_dashboard()
    )
