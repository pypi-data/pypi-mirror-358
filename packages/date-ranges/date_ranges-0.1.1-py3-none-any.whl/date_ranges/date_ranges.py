from __future__ import annotations

import datetime
import re
from collections.abc import Iterator
from typing import Any
from typing import Self

from attrs import define
from attrs import field
from attrs import validators

from .date_utils import last_date_of_month

MIN_DATE = datetime.date(datetime.MINYEAR, 1, 1)
MAX_DATE = datetime.date(9999, 12, 31)  # supported by Python, MariaDB, and PostgreSQL


class DateRangeIterator(Iterator[datetime.date]):
    def __init__(self, first_date: datetime.date, last_date: datetime.date) -> None:
        self._next_date = first_date
        self._last_date = last_date

    def __next__(self) -> datetime.date:
        if self._next_date > self._last_date:
            raise StopIteration
        this_date = self._next_date
        self._next_date += datetime.timedelta(days=1)
        return this_date


def _start_le_end(instance: DateRange, _attribute: Any, value: datetime.date) -> None:
    if value == MAX_DATE and instance.end == MIN_DATE:
        return  # special case of "empty" range
    if value > instance.end:
        raise ValueError("'start' must be <= 'end'")


@define(frozen=True, str=False)
class DateRange:
    start: datetime.date = field(
        validator=[validators.instance_of(datetime.date), _start_le_end],
    )
    end: datetime.date = field(
        default=MAX_DATE,
        validator=validators.instance_of(datetime.date),
    )

    @classmethod
    def empty(cls) -> Self:
        return cls(start=MAX_DATE, end=MIN_DATE)

    @classmethod
    def from_string(cls, s: str) -> Self:
        """
        Create a DateRange from a string of the form:
            YYYYMM a range for the given month
            YYYYMM-YYYYMM a range for the given months
            YYYYMMDD a range of a single date
            YYYYMMDD-YYYYMMDD a specific range
        Note that an optional '-' is allowed between YYYY, MM, and DD.
        Also, the '-' in the last two forms may be a ':'.
        For example, 'YYYY-MM-DD:YYYYMMDD' is acceptable.
        """
        if m := re.fullmatch(r'(\d{4})-?(\d{2})', s):
            start = datetime.date(int(m.group(1)), int(m.group(2)), 1)
            end = last_date_of_month(start)
            return cls(start, end)
        if m := re.fullmatch(
            r'(\d{4})-?(\d{2})[-:]'
            r'(\d{4})-?(\d{2})', s,
        ):
            start = datetime.date(int(m.group(1)), int(m.group(2)), 1)
            end = last_date_of_month(datetime.date(int(m.group(3)), int(m.group(4)), 1))
            return cls(start, end)
        if m := re.fullmatch(r'(\d{4})-?(\d{2})-?(\d{2})', s):
            start = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return cls(start, start)
        if m := re.fullmatch(
            r'(\d{4})-?(\d{2})-?(\d{2})[-:]'
            r'(\d{4})-?(\d{2})-?(\d{2})', s,
        ):
            start = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            end = datetime.date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
            return cls(start, end)
        raise ValueError("invalid literal for DateRange.from_string(): '{s}'")

    def __bool__(self) -> bool:
        return self.start <= self.end

    def __contains__(self, item: datetime.date) -> bool:
        if not isinstance(item, datetime.date):
            raise NotImplementedError
        if not self:
            return False
        return (self.start <= item) and (item <= self.end)

    def __iter__(self) -> Iterator[datetime.date]:
        return DateRangeIterator(self.start, self.end)

    def days(self) -> int:
        if not self:
            return 0
        return (self.end - self.start).days + 1

    def overlap(self, other: Self) -> DateRange:
        if not isinstance(other, DateRange):
            raise NotImplementedError
        if not self or not other:
            return DateRange.empty()
        latest_start = max(self.start, other.start)
        earliest_end = min(self.end, other.end)
        if earliest_end < latest_start:
            return DateRange.empty()
        return DateRange(latest_start, earliest_end)

    def _str(
            self, fmt_ym: str = '%Y%m', fmt_ymd: str = '%Y%m%d', str_to: str = '-',
    ) -> str:
        """Returns a string representation of the DateRange a la:
            'YYYYMM' - for a single, full month
            'YYYYMM-YYYYMM' - for a range of full months
            'YYYYMMDD' - for a range of a single date
            'YYYYMMDD-YYYYMMDD' - otherwise
           The actual string formats are determined by the parameters.
        """
        start_on_first = self.start.day == 1
        end_on_last = self.end.day == last_date_of_month(self.end).day
        if start_on_first and end_on_last:
            start_str = self.start.strftime(fmt_ym)
            if (self.start.year, self.start.month) == (self.end.year, self.end.month):
                retval = start_str
            else:
                retval = f"{start_str}{str_to}{self.end.strftime(fmt_ym)}"
        elif self.start == self.end:
            retval = f"{self.start.strftime(fmt_ymd)}"
        else:
            retval = f"{self.start.strftime(fmt_ymd)}{str_to}{self.end.strftime(fmt_ymd)}"
        return retval

    def str_compact(self) -> str:
        return self._str(fmt_ym='%Y%m', fmt_ymd='%Y%m%d', str_to='-')

    def str_human(self) -> str:
        """Returns a string representation of the DateRange suitable for
        including in a message to a human:
            'Month YYYY' - for a single, full month
            'Month YYYY to Month YYYY' - for a range of full months
            'YYYY-MM-DD' - for a range of a single date
            'YYYY-MM-DD to YYYY-MM-DD' - otherwise
        """
        return self._str(fmt_ym='%B %Y', fmt_ymd='%Y-%m-%d', str_to=' to ')

    def __format__(self, format_spec: str) -> str:
        if not format_spec:
            return str(self)
        format_spec_last = format_spec[-1]
        if not format_spec_last.isalpha():
            string = self.str_compact()
            string_format_spec = format_spec
        elif format_spec_last in ('C', 's'):
            string = self.str_compact()
            string_format_spec = format_spec[:-1]
        elif format_spec_last == 'H':
            string = self.str_human()
            string_format_spec = format_spec[:-1]
        else:
            raise ValueError(
                f"Unknown format code '{format_spec[0]}' "
                f"for object of type {type(self)}",
            )
        return format(string, string_format_spec)

    def __str__(self) -> str:
        return self.str_compact()


def date_range_for_month_containing(d: datetime.date) -> DateRange:
    start_date = datetime.date(d.year, d.month, 1)
    return DateRange(start_date, last_date_of_month(d))
