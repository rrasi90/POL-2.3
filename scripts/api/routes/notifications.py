"""Notification HTTP routes — Stage 32."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload
from scripts.api.schemas import NotificationPreferenceUpdateRequest


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.notifications_list(status=status, offset=offset, limit=limit)
    )


@router.get("/preferences")
def get_notification_preferences(
    boundary=Depends(get_application_boundary),
):
    return success_payload(boundary.notification_preferences_get())


@router.put("/preferences")
def update_notification_preference(
    payload: NotificationPreferenceUpdateRequest,
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.notification_preferences_update(
            event_name=payload.event_name,
            channel=payload.channel,
            is_enabled=payload.is_enabled,
        )
    )


inbox_router = APIRouter(prefix="/inbox", tags=["notifications"])


@inbox_router.get("/items")
def list_inbox_items(
    is_read: bool | None = Query(default=None),
    category: str | None = Query(default=None, max_length=32),
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.inbox_list(is_read=is_read, category=category, limit=limit, offset=offset)
    )


@inbox_router.patch("/items/{item_id}/read")
def mark_inbox_item_read(item_id: str, boundary=Depends(get_application_boundary)):
    return success_payload(boundary.inbox_mark_read(item_id=item_id))


@inbox_router.patch("/items/read-all")
def mark_all_inbox_read(boundary=Depends(get_application_boundary)):
    return success_payload(boundary.inbox_mark_all_read())
