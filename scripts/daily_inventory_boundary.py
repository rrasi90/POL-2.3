"""Thin wrapper around DailyInventoryService for application boundary consumption.

Isolates the legacy domain_services import so application_boundary.py
does not directly import scripts.domain_services.
"""

from __future__ import annotations


def get_or_create_daily_confirmation(cur, vendor_id: str, confirmation_date: str) -> dict:
    from scripts.domain_services import DailyInventoryService
    return DailyInventoryService.get_or_create_daily_confirmation(cur, vendor_id, confirmation_date)


def confirm_no_changes(cur, vendor_id: str, actor_user_id: str, confirmation_date: str, source: str = "WEB_PANEL") -> dict:
    from scripts.domain_services import DailyInventoryService
    return DailyInventoryService.confirm_no_changes(cur, vendor_id, actor_user_id, confirmation_date, source)


def confirm_with_changes(cur, vendor_id: str, actor_user_id: str, confirmation_date: str, changes: list, source: str = "WEB_PANEL") -> dict:
    from scripts.domain_services import DailyInventoryService
    return DailyInventoryService.confirm_with_changes(cur, vendor_id, actor_user_id, confirmation_date, changes, source)
