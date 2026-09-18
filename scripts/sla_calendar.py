"""Canonical Ahvaz wholesale-market working-time SLA calendar."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
import zoneinfo

TEHRAN_TZ = zoneinfo.ZoneInfo("Asia/Tehran")
WORK_START = time(8, 0)
WORK_END = time(18, 0)
CALENDAR_KEY = "AHVAZ_WHOLESALE"


def is_working_day(day: date, holidays: set[date] | None = None) -> bool:
    return day.weekday() != 4 and not (holidays and day in holidays)


def calculate_sla_deadline(
    submitted_at: datetime,
    duration_hours: float = 2.0,
    holidays: set[date] | None = None,
) -> datetime:
    if duration_hours < 0:
        raise ValueError("SLA duration cannot be negative.")

    remaining_seconds = duration_hours * 3600.0
    current = submitted_at.astimezone(TEHRAN_TZ)

    if remaining_seconds == 0:
        return current

    while remaining_seconds > 0:
        if not is_working_day(current.date(), holidays):
            current = datetime.combine(
                current.date() + timedelta(days=1),
                WORK_START,
                tzinfo=TEHRAN_TZ,
            )
            continue

        if current.time() < WORK_START:
            current = datetime.combine(
                current.date(), WORK_START, tzinfo=TEHRAN_TZ
            )
            continue

        if current.time() >= WORK_END:
            current = datetime.combine(
                current.date() + timedelta(days=1),
                WORK_START,
                tzinfo=TEHRAN_TZ,
            )
            continue

        end_of_day = datetime.combine(
            current.date(), WORK_END, tzinfo=TEHRAN_TZ
        )
        available_today = (end_of_day - current).total_seconds()

        if remaining_seconds <= available_today:
            return current + timedelta(seconds=remaining_seconds)

        remaining_seconds -= available_today
        current = datetime.combine(
            current.date() + timedelta(days=1),
            WORK_START,
            tzinfo=TEHRAN_TZ,
        )

    return current


def load_operational_holidays(cur, calendar_key: str = CALENDAR_KEY) -> set[date]:
    cur.execute(
        """
        SELECT holiday_date
        FROM operational_holidays
        WHERE calendar_key = %s
          AND is_active = TRUE
        ORDER BY holiday_date
        """,
        (calendar_key,),
    )
    return {row["holiday_date"] for row in cur.fetchall()}
