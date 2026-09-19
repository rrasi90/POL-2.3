"""Field Tasks HTTP routes — Stage 35."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import FieldTaskCreateRequest, FieldTaskUpdateRequest


router = APIRouter(prefix="/field", tags=["field"])


@router.get("/tasks")
def list_field_tasks(
    task_status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.field_tasks_list(status=task_status, offset=offset, limit=limit)
    )


@router.get("/tasks/{task_id}")
def get_field_task(
    task_id: UUID,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.field_task_get(task_id=str(task_id))
    )


@router.patch("/tasks/{task_id}")
def update_field_task(
    task_id: UUID,
    payload: FieldTaskUpdateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.field_task_update(
            task_id=str(task_id),
            status=payload.status,
            notes=payload.notes,
        )
    )


@router.post("/tasks", status_code=201)
def create_field_task(
    payload: FieldTaskCreateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.field_task_create(
            task_type=payload.task_type,
            assigned_to_user_id=payload.assigned_to_user_id,
            retailer_id=payload.retailer_id,
            vendor_id=payload.vendor_id,
            notes=payload.notes,
        )
    )
