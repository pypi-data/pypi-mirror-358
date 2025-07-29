import datetime

import pytest
from date_ranges import first_weekday_of_month
from date_ranges import last_weekday_of_month
from date_ranges import weekday_after
from date_ranges import weekday_before

VALID_WEEKDAY_AFTER = [
    (datetime.date(2025, 6, 26), 0, datetime.date(2025, 6, 30)),
    (datetime.date(2025, 6, 26), 1, datetime.date(2025, 7, 1)),
    (datetime.date(2025, 6, 26), 2, datetime.date(2025, 7, 2)),
    (datetime.date(2025, 6, 26), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 6, 26), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 6, 26), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 6, 26), 6, datetime.date(2025, 6, 29)),
    (datetime.date(2025, 6, 27), 0, datetime.date(2025, 6, 30)),
    (datetime.date(2025, 6, 27), 1, datetime.date(2025, 7, 1)),
    (datetime.date(2025, 6, 27), 2, datetime.date(2025, 7, 2)),
    (datetime.date(2025, 6, 27), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 6, 27), 4, datetime.date(2025, 7, 4)),
    (datetime.date(2025, 6, 27), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 6, 27), 6, datetime.date(2025, 6, 29)),
    (datetime.date(2025, 6, 28), 0, datetime.date(2025, 6, 30)),
    (datetime.date(2025, 6, 28), 1, datetime.date(2025, 7, 1)),
    (datetime.date(2025, 6, 28), 2, datetime.date(2025, 7, 2)),
    (datetime.date(2025, 6, 28), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 6, 28), 4, datetime.date(2025, 7, 4)),
    (datetime.date(2025, 6, 28), 5, datetime.date(2025, 7, 5)),
    (datetime.date(2025, 6, 28), 6, datetime.date(2025, 6, 29)),
    (datetime.date(2025, 6, 29), 0, datetime.date(2025, 6, 30)),
    (datetime.date(2025, 6, 29), 1, datetime.date(2025, 7, 1)),
    (datetime.date(2025, 6, 29), 2, datetime.date(2025, 7, 2)),
    (datetime.date(2025, 6, 29), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 6, 29), 4, datetime.date(2025, 7, 4)),
    (datetime.date(2025, 6, 29), 5, datetime.date(2025, 7, 5)),
    (datetime.date(2025, 6, 29), 6, datetime.date(2025, 7, 6)),
    (datetime.date(2025, 6, 30), 0, datetime.date(2025, 7, 7)),
    (datetime.date(2025, 6, 30), 1, datetime.date(2025, 7, 1)),
    (datetime.date(2025, 6, 30), 2, datetime.date(2025, 7, 2)),
    (datetime.date(2025, 6, 30), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 6, 30), 4, datetime.date(2025, 7, 4)),
    (datetime.date(2025, 6, 30), 5, datetime.date(2025, 7, 5)),
    (datetime.date(2025, 6, 30), 6, datetime.date(2025, 7, 6)),
    (datetime.date(2025, 7, 1), 0, datetime.date(2025, 7, 7)),
    (datetime.date(2025, 7, 1), 1, datetime.date(2025, 7, 8)),
    (datetime.date(2025, 7, 1), 2, datetime.date(2025, 7, 2)),
    (datetime.date(2025, 7, 1), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 7, 1), 4, datetime.date(2025, 7, 4)),
    (datetime.date(2025, 7, 1), 5, datetime.date(2025, 7, 5)),
    (datetime.date(2025, 7, 1), 6, datetime.date(2025, 7, 6)),
    (datetime.date(2025, 7, 2), 0, datetime.date(2025, 7, 7)),
    (datetime.date(2025, 7, 2), 1, datetime.date(2025, 7, 8)),
    (datetime.date(2025, 7, 2), 2, datetime.date(2025, 7, 9)),
    (datetime.date(2025, 7, 2), 3, datetime.date(2025, 7, 3)),
    (datetime.date(2025, 7, 2), 4, datetime.date(2025, 7, 4)),
    (datetime.date(2025, 7, 2), 5, datetime.date(2025, 7, 5)),
    (datetime.date(2025, 7, 2), 6, datetime.date(2025, 7, 6)),
]


@pytest.mark.parametrize('valid_weekday_after', VALID_WEEKDAY_AFTER)
def test_valid_weekday_after(
        valid_weekday_after: tuple[datetime.date, int, datetime.date],
) -> None:
    start_date, weekday, expected_date = valid_weekday_after
    actual_date = weekday_after(start_date=start_date, weekday=weekday)
    assert actual_date == expected_date


@pytest.mark.parametrize('invalid_weekday', [-2, -1, 7, 8])
def test_invalid_weekday_after(invalid_weekday: int) -> None:
    with pytest.raises(ValueError, match=r'weekday must be between 0 and 6'):
        weekday_after(start_date=datetime.date(2025, 6, 26), weekday=invalid_weekday)


VALID_WEEKDAY_BEFORE = [
    (datetime.date(2025, 6, 26), 0, datetime.date(2025, 6, 23)),
    (datetime.date(2025, 6, 26), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 6, 26), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 6, 26), 3, datetime.date(2025, 6, 19)),
    (datetime.date(2025, 6, 26), 4, datetime.date(2025, 6, 20)),
    (datetime.date(2025, 6, 26), 5, datetime.date(2025, 6, 21)),
    (datetime.date(2025, 6, 26), 6, datetime.date(2025, 6, 22)),
    (datetime.date(2025, 6, 27), 0, datetime.date(2025, 6, 23)),
    (datetime.date(2025, 6, 27), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 6, 27), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 6, 27), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 6, 27), 4, datetime.date(2025, 6, 20)),
    (datetime.date(2025, 6, 27), 5, datetime.date(2025, 6, 21)),
    (datetime.date(2025, 6, 27), 6, datetime.date(2025, 6, 22)),
    (datetime.date(2025, 6, 28), 0, datetime.date(2025, 6, 23)),
    (datetime.date(2025, 6, 28), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 6, 28), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 6, 28), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 6, 28), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 6, 28), 5, datetime.date(2025, 6, 21)),
    (datetime.date(2025, 6, 28), 6, datetime.date(2025, 6, 22)),
    (datetime.date(2025, 6, 29), 0, datetime.date(2025, 6, 23)),
    (datetime.date(2025, 6, 29), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 6, 29), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 6, 29), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 6, 29), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 6, 29), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 6, 29), 6, datetime.date(2025, 6, 22)),
    (datetime.date(2025, 6, 30), 0, datetime.date(2025, 6, 23)),
    (datetime.date(2025, 6, 30), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 6, 30), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 6, 30), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 6, 30), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 6, 30), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 6, 30), 6, datetime.date(2025, 6, 29)),
    (datetime.date(2025, 7, 1), 0, datetime.date(2025, 6, 30)),
    (datetime.date(2025, 7, 1), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 7, 1), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 7, 1), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 7, 1), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 7, 1), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 7, 1), 6, datetime.date(2025, 6, 29)),
    (datetime.date(2025, 7, 2), 0, datetime.date(2025, 6, 30)),
    (datetime.date(2025, 7, 2), 1, datetime.date(2025, 7, 1)),
    (datetime.date(2025, 7, 2), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 7, 2), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 7, 2), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 7, 2), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 7, 2), 6, datetime.date(2025, 6, 29)),
]


@pytest.mark.parametrize('valid_weekday_before', VALID_WEEKDAY_BEFORE)
def test_valid_weekday_before(
        valid_weekday_before: tuple[datetime.date, int, datetime.date],
) -> None:
    start_date, weekday, expected_date = valid_weekday_before
    actual_date = weekday_before(start_date=start_date, weekday=weekday)
    assert actual_date == expected_date


@pytest.mark.parametrize('invalid_weekday', [-2, -1, 7, 8])
def test_invalid_weekday_before(invalid_weekday: int) -> None:
    with pytest.raises(ValueError, match=r'weekday must be between 0 and 6'):
        weekday_before(start_date=datetime.date(2025, 6, 26), weekday=invalid_weekday)


VALID_FIRST_WEEKDAY = [
    (datetime.date(2025, 9, 1), 0, datetime.date(2025, 9, 1)),  # Mon
    (datetime.date(2025, 9, 1), 1, datetime.date(2025, 9, 2)),
    (datetime.date(2025, 9, 1), 2, datetime.date(2025, 9, 3)),
    (datetime.date(2025, 9, 1), 3, datetime.date(2025, 9, 4)),
    (datetime.date(2025, 9, 1), 4, datetime.date(2025, 9, 5)),
    (datetime.date(2025, 9, 1), 5, datetime.date(2025, 9, 6)),
    (datetime.date(2025, 9, 1), 6, datetime.date(2025, 9, 7)),
    (datetime.date(2025, 4, 1), 0, datetime.date(2025, 4, 7)),  # Tue
    (datetime.date(2025, 4, 1), 1, datetime.date(2025, 4, 1)),
    (datetime.date(2025, 4, 1), 2, datetime.date(2025, 4, 2)),
    (datetime.date(2025, 4, 1), 3, datetime.date(2025, 4, 3)),
    (datetime.date(2025, 4, 1), 4, datetime.date(2025, 4, 4)),
    (datetime.date(2025, 4, 1), 5, datetime.date(2025, 4, 5)),
    (datetime.date(2025, 4, 1), 6, datetime.date(2025, 4, 6)),
    (datetime.date(2025, 1, 1), 0, datetime.date(2025, 1, 6)),  # Wed
    (datetime.date(2025, 1, 1), 1, datetime.date(2025, 1, 7)),
    (datetime.date(2025, 1, 1), 2, datetime.date(2025, 1, 1)),
    (datetime.date(2025, 1, 1), 3, datetime.date(2025, 1, 2)),
    (datetime.date(2025, 1, 1), 4, datetime.date(2025, 1, 3)),
    (datetime.date(2025, 1, 1), 5, datetime.date(2025, 1, 4)),
    (datetime.date(2025, 1, 1), 6, datetime.date(2025, 1, 5)),
    (datetime.date(2025, 5, 1), 0, datetime.date(2025, 5, 5)),  # Thu
    (datetime.date(2025, 5, 1), 1, datetime.date(2025, 5, 6)),
    (datetime.date(2025, 5, 1), 2, datetime.date(2025, 5, 7)),
    (datetime.date(2025, 5, 1), 3, datetime.date(2025, 5, 1)),
    (datetime.date(2025, 5, 1), 4, datetime.date(2025, 5, 2)),
    (datetime.date(2025, 5, 1), 5, datetime.date(2025, 5, 3)),
    (datetime.date(2025, 5, 1), 6, datetime.date(2025, 5, 4)),
    (datetime.date(2025, 8, 1), 0, datetime.date(2025, 8, 4)),  # Fri
    (datetime.date(2025, 8, 1), 1, datetime.date(2025, 8, 5)),
    (datetime.date(2025, 8, 1), 2, datetime.date(2025, 8, 6)),
    (datetime.date(2025, 8, 1), 3, datetime.date(2025, 8, 7)),
    (datetime.date(2025, 8, 1), 4, datetime.date(2025, 8, 1)),
    (datetime.date(2025, 8, 1), 5, datetime.date(2025, 8, 2)),
    (datetime.date(2025, 8, 1), 6, datetime.date(2025, 8, 3)),
    (datetime.date(2025, 2, 1), 0, datetime.date(2025, 2, 3)),  # Sat
    (datetime.date(2025, 2, 1), 1, datetime.date(2025, 2, 4)),
    (datetime.date(2025, 2, 1), 2, datetime.date(2025, 2, 5)),
    (datetime.date(2025, 2, 1), 3, datetime.date(2025, 2, 6)),
    (datetime.date(2025, 2, 1), 4, datetime.date(2025, 2, 7)),
    (datetime.date(2025, 2, 1), 5, datetime.date(2025, 2, 1)),
    (datetime.date(2025, 2, 1), 6, datetime.date(2025, 2, 2)),
    (datetime.date(2025, 6, 1), 0, datetime.date(2025, 6, 2)),  # Sun
    (datetime.date(2025, 6, 1), 1, datetime.date(2025, 6, 3)),
    (datetime.date(2025, 6, 1), 2, datetime.date(2025, 6, 4)),
    (datetime.date(2025, 6, 1), 3, datetime.date(2025, 6, 5)),
    (datetime.date(2025, 6, 1), 4, datetime.date(2025, 6, 6)),
    (datetime.date(2025, 6, 1), 5, datetime.date(2025, 6, 7)),
    (datetime.date(2025, 6, 1), 6, datetime.date(2025, 6, 1)),
]


@pytest.mark.parametrize('first_weekday', VALID_FIRST_WEEKDAY)
def test_first_weekday_of_month(
        first_weekday: tuple[datetime.date, int, datetime.date],
) -> None:
    date_in_month, weekday, expected_date = first_weekday
    actual_date = first_weekday_of_month(date_in_month=date_in_month, weekday=weekday)
    assert actual_date == expected_date

VALID_LAST_WEEKDAY = [
    (datetime.date(2025, 6, 1), 0, datetime.date(2025, 6, 30)),  # Mon
    (datetime.date(2025, 6, 1), 1, datetime.date(2025, 6, 24)),
    (datetime.date(2025, 6, 1), 2, datetime.date(2025, 6, 25)),
    (datetime.date(2025, 6, 1), 3, datetime.date(2025, 6, 26)),
    (datetime.date(2025, 6, 1), 4, datetime.date(2025, 6, 27)),
    (datetime.date(2025, 6, 1), 5, datetime.date(2025, 6, 28)),
    (datetime.date(2025, 6, 1), 6, datetime.date(2025, 6, 29)),
    (datetime.date(2025, 9, 1), 0, datetime.date(2025, 9, 29)),  # Tue
    (datetime.date(2025, 9, 1), 1, datetime.date(2025, 9, 30)),
    (datetime.date(2025, 9, 1), 2, datetime.date(2025, 9, 24)),
    (datetime.date(2025, 9, 1), 3, datetime.date(2025, 9, 25)),
    (datetime.date(2025, 9, 1), 4, datetime.date(2025, 9, 26)),
    (datetime.date(2025, 9, 1), 5, datetime.date(2025, 9, 27)),
    (datetime.date(2025, 9, 1), 6, datetime.date(2025, 9, 28)),
    (datetime.date(2025, 4, 1), 0, datetime.date(2025, 4, 28)),  # Wed
    (datetime.date(2025, 4, 1), 1, datetime.date(2025, 4, 29)),
    (datetime.date(2025, 4, 1), 2, datetime.date(2025, 4, 30)),
    (datetime.date(2025, 4, 1), 3, datetime.date(2025, 4, 24)),
    (datetime.date(2025, 4, 1), 4, datetime.date(2025, 4, 25)),
    (datetime.date(2025, 4, 1), 5, datetime.date(2025, 4, 26)),
    (datetime.date(2025, 4, 1), 6, datetime.date(2025, 4, 27)),
    (datetime.date(2025, 7, 1), 0, datetime.date(2025, 7, 28)),  # Thu
    (datetime.date(2025, 7, 1), 1, datetime.date(2025, 7, 29)),
    (datetime.date(2025, 7, 1), 2, datetime.date(2025, 7, 30)),
    (datetime.date(2025, 7, 1), 3, datetime.date(2025, 7, 31)),
    (datetime.date(2025, 7, 1), 4, datetime.date(2025, 7, 25)),
    (datetime.date(2025, 7, 1), 5, datetime.date(2025, 7, 26)),
    (datetime.date(2025, 7, 1), 6, datetime.date(2025, 7, 27)),
    (datetime.date(2025, 2, 1), 0, datetime.date(2025, 2, 24)),  # Fri
    (datetime.date(2025, 2, 1), 1, datetime.date(2025, 2, 25)),
    (datetime.date(2025, 2, 1), 2, datetime.date(2025, 2, 26)),
    (datetime.date(2025, 2, 1), 3, datetime.date(2025, 2, 27)),
    (datetime.date(2025, 2, 1), 4, datetime.date(2025, 2, 28)),
    (datetime.date(2025, 2, 1), 5, datetime.date(2025, 2, 22)),
    (datetime.date(2025, 2, 1), 6, datetime.date(2025, 2, 23)),
    (datetime.date(2025, 5, 1), 0, datetime.date(2025, 5, 26)),  # Sat
    (datetime.date(2025, 5, 1), 1, datetime.date(2025, 5, 27)),
    (datetime.date(2025, 5, 1), 2, datetime.date(2025, 5, 28)),
    (datetime.date(2025, 5, 1), 3, datetime.date(2025, 5, 29)),
    (datetime.date(2025, 5, 1), 4, datetime.date(2025, 5, 30)),
    (datetime.date(2025, 5, 1), 5, datetime.date(2025, 5, 31)),
    (datetime.date(2025, 5, 1), 6, datetime.date(2025, 5, 25)),
    (datetime.date(2025, 8, 1), 0, datetime.date(2025, 8, 25)),  # Sun
    (datetime.date(2025, 8, 1), 1, datetime.date(2025, 8, 26)),
    (datetime.date(2025, 8, 1), 2, datetime.date(2025, 8, 27)),
    (datetime.date(2025, 8, 1), 3, datetime.date(2025, 8, 28)),
    (datetime.date(2025, 8, 1), 4, datetime.date(2025, 8, 29)),
    (datetime.date(2025, 8, 1), 5, datetime.date(2025, 8, 30)),
    (datetime.date(2025, 8, 1), 6, datetime.date(2025, 8, 31)),
]


@pytest.mark.parametrize('last_weekday', VALID_LAST_WEEKDAY)
def test_last_weekday_of_month(
        last_weekday: tuple[datetime.date, int, datetime.date],
) -> None:
    date_in_month, weekday, expected_date = last_weekday
    actual_date = last_weekday_of_month(date_in_month=date_in_month, weekday=weekday)
    assert actual_date == expected_date
