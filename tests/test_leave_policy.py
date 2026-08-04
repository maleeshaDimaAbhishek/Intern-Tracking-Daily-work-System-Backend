from datetime import date

from app.services.leave_policy import get_leave_period, requires_medical_certificate


def test_one_day_sick_leave_does_not_require_certificate():
    day = date(2026, 7, 30)
    assert requires_medical_certificate("Sick Leave", day, day) is False


def test_two_day_sick_leave_does_not_require_certificate():
    assert requires_medical_certificate(
        "Sick Leave", date(2026, 7, 30), date(2026, 7, 31)
    ) is False


def test_three_day_sick_leave_requires_certificate():
    assert requires_medical_certificate(
        "Sick Leave", date(2026, 7, 30), date(2026, 8, 1)
    ) is True


def test_non_sick_leave_does_not_require_certificate():
    assert requires_medical_certificate(
        "Personal Leave", date(2026, 7, 30), date(2026, 8, 1)
    ) is False


def test_range_leave_period_uses_start_and_end_dates():
    start = date(2026, 8, 3)
    end = date(2026, 8, 5)
    assert get_leave_period("Personal Leave", start, end, None) == (start, end)


def test_single_day_leave_period_uses_the_same_date_for_both_bounds():
    day = date(2026, 8, 3)
    assert get_leave_period("Emergency Leave", None, None, day) == (day, day)


def test_half_day_leave_period_uses_the_selected_date():
    day = date(2026, 8, 3)
    assert get_leave_period("Half-Day Leave", None, None, day) == (day, day)
