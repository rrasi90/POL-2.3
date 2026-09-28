"""Authenticated pilot analytics HTTP routes."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query

from scripts.api.dependencies import get_application_boundary
from scripts.api.errors import success_payload

router = APIRouter(prefix="/ops/analytics", tags=["ops-analytics"])


@router.get("")
def pilot_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    boundary=Depends(get_application_boundary),
):
    return success_payload(
        boundary.ops_analytics(start_date=start_date, end_date=end_date)
    )


@router.get("/weekly")
def pilot_analytics_weekly(
    snapshot_date: date | None = Query(default=None),
    boundary=Depends(get_application_boundary),
):
    target = snapshot_date or date.today()
    if target < date(2020, 1, 1) or target > date.today() + timedelta(days=1):
        raise ValueError("snapshot_date is outside the supported range.")
    return success_payload(boundary.ops_analytics_week(snapshot_date=target))
