"""
POL SLA Working Hours Calendar Runtime Verification Suite
Tests:
- Ahvaz B2B wholesale operational hours: Sat-Thu 08:00 to 18:00 (Asia/Tehran)
- Friday weekly weekend exclusion
- Within-day 2-hour SLA deadline calculation
- End-of-day rollover (e.g. 17:30 -> 09:30 next working morning)
- Weekend rollover (Thursday evening -> Saturday morning)
- Official holiday exclusion
- After-hours order submission timer initiation
- Timeout evaluation predicate
"""

import sys
from datetime import datetime, date, time, timedelta
import zoneinfo

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TEHRAN_TZ = zoneinfo.ZoneInfo("Asia/Tehran")

# Ahvaz Wholesale Market Operating Schedule
WORK_START = time(8, 0)
WORK_END = time(18, 0)
WORKING_DAYS = {5, 6, 0, 1, 2, 3}  # Sat=5, Sun=6, Mon=0, Tue=1, Wed=2, Thu=3 (Python weekday: Mon=0, Sun=6)
# In Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
# Saturday=5, Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4 (Excluded)

def is_working_day(dt: datetime, holidays: set = None) -> bool:
    if holidays and dt.date() in holidays:
        return False
    return dt.weekday() != 4  # Friday is excluded

def calculate_sla_deadline(submitted_at: datetime, duration_hours: float = 2.0, holidays: set = None) -> datetime:
    """Calculates SLA deadline taking into account working hours, weekends, and holidays."""
    remaining_seconds = duration_hours * 3600.0
    curr = submitted_at.astimezone(TEHRAN_TZ)

    while remaining_seconds > 0:
        # If not a working day, advance to next day 08:00
        if not is_working_day(curr, holidays):
            next_day = curr.date() + timedelta(days=1)
            curr = datetime.combine(next_day, WORK_START, tzinfo=TEHRAN_TZ)
            continue

        # If before working hours, advance to 08:00 today
        if curr.time() < WORK_START:
            curr = datetime.combine(curr.date(), WORK_START, tzinfo=TEHRAN_TZ)

        # If after working hours, advance to next day 08:00
        if curr.time() >= WORK_END:
            next_day = curr.date() + timedelta(days=1)
            curr = datetime.combine(next_day, WORK_START, tzinfo=TEHRAN_TZ)
            continue

        # Currently in working hours
        end_of_day = datetime.combine(curr.date(), WORK_END, tzinfo=TEHRAN_TZ)
        available_today = (end_of_day - curr).total_seconds()

        if remaining_seconds <= available_today:
            curr = curr + timedelta(seconds=remaining_seconds)
            remaining_seconds = 0
        else:
            remaining_seconds -= available_today
            next_day = curr.date() + timedelta(days=1)
            curr = datetime.combine(next_day, WORK_START, tzinfo=TEHRAN_TZ)

    return curr

def test_sla_calendar():
    print("================================================================")
    print("POL SLA WORKING CALENDAR & TIMEOUT RUNTIME VERIFICATION")
    print("================================================================")

    # 1. Standard Within-Day Calculation (Monday 10:00 -> Monday 12:00)
    print("\n[TEST 1] Standard Within-Day SLA (Monday 10:00 + 2 hrs)...")
    t1 = datetime(2026, 9, 14, 10, 0, tzinfo=TEHRAN_TZ) # Monday
    d1 = calculate_sla_deadline(t1, 2.0)
    expected_d1 = datetime(2026, 9, 14, 12, 0, tzinfo=TEHRAN_TZ)
    assert d1 == expected_d1, f"Expected {expected_d1}, got {d1}"
    print(f"  [PASS] Within-day deadline: {t1.strftime('%Y-%m-%d %H:%M')} -> {d1.strftime('%Y-%m-%d %H:%M')}")

    # 2. End-of-Day Rollover (Tuesday 17:30 -> Wednesday 09:30)
    print("\n[TEST 2] End-of-Day Rollover (Tuesday 17:30 + 2 hrs)...")
    t2 = datetime(2026, 9, 15, 17, 30, tzinfo=TEHRAN_TZ) # Tuesday
    d2 = calculate_sla_deadline(t2, 2.0)
    expected_d2 = datetime(2026, 9, 16, 9, 30, tzinfo=TEHRAN_TZ) # Wednesday 09:30
    assert d2 == expected_d2, f"Expected {expected_d2}, got {d2}"
    print(f"  [PASS] End-of-day rollover: {t2.strftime('%Y-%m-%d %H:%M')} -> {d2.strftime('%Y-%m-%d %H:%M')}")

    # 3. Weekend (Friday) Skip (Thursday 17:00 -> Saturday 09:00)
    print("\n[TEST 3] Friday Weekend Skip (Thursday 17:00 + 2 hrs)...")
    t3 = datetime(2026, 9, 17, 17, 0, tzinfo=TEHRAN_TZ) # Thursday
    d3 = calculate_sla_deadline(t3, 2.0)
    # 1 hr on Thursday (17:00-18:00), Friday skipped, remaining 1 hr on Saturday (08:00-09:00)
    expected_d3 = datetime(2026, 9, 19, 9, 0, tzinfo=TEHRAN_TZ) # Saturday 09:00
    assert d3 == expected_d3, f"Expected {expected_d3}, got {d3}"
    print(f"  [PASS] Weekend skip: {t3.strftime('%a %H:%M')} -> {d3.strftime('%a %H:%M')} (Friday excluded).")

    # 4. Out-of-Hours Submission (Sunday 21:00 -> Monday 10:00)
    print("\n[TEST 4] After-Hours Submission (Sunday 21:00 + 2 hrs)...")
    t4 = datetime(2026, 9, 13, 21, 0, tzinfo=TEHRAN_TZ) # Sunday night
    d4 = calculate_sla_deadline(t4, 2.0)
    expected_d4 = datetime(2026, 9, 14, 10, 0, tzinfo=TEHRAN_TZ) # Monday 10:00
    assert d4 == expected_d4, f"Expected {expected_d4}, got {d4}"
    print(f"  [PASS] After-hours submission: {t4.strftime('%a %H:%M')} starts Mon 08:00 -> {d4.strftime('%a %H:%M')}")

    # 5. Official Holiday Exclusion
    print("\n[TEST 5] Official Public Holiday Exclusion...")
    holidays = {date(2026, 9, 16)} # Wednesday is official holiday
    t5 = datetime(2026, 9, 15, 17, 30, tzinfo=TEHRAN_TZ) # Tuesday 17:30
    d5 = calculate_sla_deadline(t5, 2.0, holidays=holidays)
    # 30 min on Tue, Wed is holiday, remaining 1.5 hr on Thu morning -> Thu 09:30
    expected_d5 = datetime(2026, 9, 17, 9, 30, tzinfo=TEHRAN_TZ) # Thursday 09:30
    assert d5 == expected_d5, f"Expected {expected_d5}, got {d5}"
    print(f"  [PASS] Holiday exclusion: Wed holiday skipped -> {d5.strftime('%a %Y-%m-%d %H:%M')}")

    # 6. Timeout Evaluation Predicate
    print("\n[TEST 6] Timeout Evaluation Predicate (now > deadline)...")
    check_time_ontime = datetime(2026, 9, 14, 11, 45, tzinfo=TEHRAN_TZ)
    check_time_late = datetime(2026, 9, 14, 12, 1, tzinfo=TEHRAN_TZ)
    assert check_time_ontime <= d1, "11:45 should be within 12:00 deadline"
    assert check_time_late > d1, "12:01 should breach 12:00 deadline"
    print("  [PASS] Timeout predicate correctly discriminates active vs expired SLA.")

    print("\n================================================================")
    print("ALL SLA WORKING CALENDAR TESTS PASSED SUCCESSFULLY!")
    print("================================================================")
    return True

if __name__ == "__main__":
    test_sla_calendar()
