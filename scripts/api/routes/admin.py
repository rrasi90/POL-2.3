"""Admin-only HTTP routes — audit logs and exception dashboard."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from uuid import UUID

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

from scripts.api.schemas import BroadcastCreateRequest, BroadcastDispatchRequest, CategoryCreateRequest, CategoryUpdateRequest


@router.post("/broadcasts", status_code=201)
def create_broadcast(
    payload: BroadcastCreateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_broadcast_create(
            title=payload.title,
            body=payload.body,
            target_criteria=payload.target_criteria,
            channel=payload.channel,
            priority=payload.priority,
            scheduled_at=payload.scheduled_at,
        )
    )


@router.post("/broadcasts/{broadcast_id}/dispatch")
def dispatch_broadcast(
    broadcast_id: UUID,
    payload: BroadcastDispatchRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.admin_broadcast_dispatch(
            broadcast_id=str(broadcast_id),
            approve=payload.approve,
        )
    )


@router.post("/categories", status_code=201)
def create_category(payload: CategoryCreateRequest, boundary=Depends(get_application_boundary)):
    return success_payload(boundary.admin_category_create(
        name_fa=payload.name_fa, slug=payload.slug, icon_url=payload.icon_url, display_order=payload.display_order
    ))


@router.patch("/categories/{category_id}")
def update_category(category_id: UUID, payload: CategoryUpdateRequest, boundary=Depends(get_application_boundary)):
    return success_payload(boundary.admin_category_update(
        category_id=str(category_id), name_fa=payload.name_fa, slug=payload.slug,
        icon_url=payload.icon_url, display_order=payload.display_order
    ))
