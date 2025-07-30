import datetime

import pytest
from date_ranges import DateRange


def test_date_in_range() -> None:
    d = datetime.date(2022, 9, 2)
    date_range = DateRange(datetime.date(2022, 9, 1))
    assert d in date_range


def test_date_in_range_false() -> None:
    d = datetime.date(2022, 9, 2)
    date_range = DateRange(
        datetime.date(2022, 8, 24),
        datetime.date(2022, 8, 31),
    )
    assert d not in date_range


def test_date_range_bool_d1_true() -> None:
    d1 = DateRange(
        start=datetime.date(2023, 8, 27),
        end=datetime.date(2023, 8, 27),
    )
    assert d1


def test_date_range_bool_d2_true() -> None:
    d2 = DateRange(
        start=datetime.date(2023, 8, 1),
        end=datetime.date(2023, 8, 2),
    )
    assert d2


def test_date_range_empty_false() -> None:
    empty = DateRange.empty()
    assert not empty


def test_date_range_str_compact_1() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert d.str_compact() == '202311'


def test_date_range_str_compact_2() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2024, 1, 31),
    )
    assert d.str_compact() == '202311-202401'


def test_date_range_str_compact_3() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2024, 1, 11),
    )
    assert d.str_compact() == '20231101-20240111'


def test_date_range_str_human_1() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert d.str_human() == 'November 2023'


def test_date_range_str_human_2() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2024, 1, 31),
    )
    assert d.str_human() == 'November 2023 to January 2024'


def test_date_range_str_human_3() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2024, 1, 11),
    )
    assert d.str_human() == '2023-11-01 to 2024-01-11'


def test_date_range_str_compact_format_1() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert f'{d}' == '202311'


def test_date_range_str_compact_format_2() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert f'{d:C}' == '202311'


def test_date_range_str_compact_format_3() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert f'{d:_^10C}' == '__202311__'


def test_date_range_str_human_format_1() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert f'{d:H}' == 'November 2023'


def test_date_range_str_1() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert str(d) == '202311'


def test_date_range_repr_1() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    assert repr(d) == (
        'DateRange(start=datetime.date(2023, 11, 1), '
        'end=datetime.date(2023, 11, 30))'
    )


def test_date_range_bad_format() -> None:
    d = DateRange(
        start=datetime.date(2023, 11, 1),
        end=datetime.date(2023, 11, 30),
    )
    with pytest.raises(
        ValueError,
        match="Unknown format code 'Q' for object "
              "of type .*DateRange",
    ):
        print(f'{d:Q}')


def test_date_range_overlap_1() -> None:
    d1 = DateRange.from_string('202311')
    d2 = DateRange.from_string('202311-202312')
    overlap = d1.overlap(d2)
    assert overlap == d1


def test_date_range_overlap_none() -> None:
    d1 = DateRange.from_string('202311')
    d2 = DateRange.from_string('202312')
    overlap = d1.overlap(d2)
    assert overlap == DateRange.empty()
