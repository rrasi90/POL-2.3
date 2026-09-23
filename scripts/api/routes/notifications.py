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
