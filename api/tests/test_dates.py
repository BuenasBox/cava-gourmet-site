import calendar
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _dates as dates


def test_costa_rica_today_matches_utc_date_at_midday():
    # 2026-09-29 12:00:00 UTC -> CR local is 2026-09-29 06:00 -> same calendar day
    ts = calendar.timegm((2026, 9, 29, 12, 0, 0))
    assert dates.costa_rica_today(ts) == "29/09/2026"


def test_costa_rica_today_rolls_back_near_utc_midnight():
    # 2026-09-29 05:00:00 UTC -> CR local is 2026-09-28 23:00 -> previous calendar day
    ts = calendar.timegm((2026, 9, 29, 5, 0, 0))
    assert dates.costa_rica_today(ts) == "28/09/2026"


def test_costa_rica_today_boundary_exactly_6am_utc():
    # 06:00 UTC is exactly CR local midnight -> new calendar day starts here
    ts = calendar.timegm((2026, 9, 29, 6, 0, 0))
    assert dates.costa_rica_today(ts) == "29/09/2026"


def test_costa_rica_today_just_before_boundary():
    ts = calendar.timegm((2026, 9, 29, 5, 59, 59))
    assert dates.costa_rica_today(ts) == "28/09/2026"
