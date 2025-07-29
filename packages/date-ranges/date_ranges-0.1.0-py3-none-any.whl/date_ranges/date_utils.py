import datetime
from calendar import monthrange


def ordinal(n: int) -> str:
    """Return a string that is the given number followed by the
    appropriate suffix to be an ordinal number.  Examples:
         1 ->   '1st'
        12 ->  '12th'
       153 -> '153rd'
    """
    tens = (n // 10) % 10
    ones = n % 10
    suffixes = ('th', 'st', 'nd', 'rd')
    return f'{n}{suffixes[(tens != 1) * (ones < 4) * ones]}'


def month_ordinal_day(d: datetime.date) -> str:
    """For a given date, return a string that is the full month name
    followed by the ordinal version of the day.  Example:
        datetime.date(1992, 4, 10)  ->  'April 10th'
    """
    month = d.strftime('%B')
    return f'{month} {ordinal(d.day)}'


def last_date_of_month(d: datetime.date) -> datetime.date:
    year = d.year
    month = d.month
    last_day_of_month = monthrange(year, month)[1]
    return datetime.date(year, month, last_day_of_month)


def weekday_after(start_date: datetime.date, weekday: int) -> datetime.date:
    if not (0 <= weekday <= 6):
        raise ValueError('weekday must be between 0 and 6')
    this_weekday = start_date.weekday()
    days_to_advance = 1 + (weekday - this_weekday - 1) % 7
    retval = start_date + datetime.timedelta(days=days_to_advance)
    return retval


def weekday_before(start_date: datetime.date, weekday: int) -> datetime.date:
    if not (0 <= weekday <= 6):
        raise ValueError('weekday must be between 0 and 6')
    this_weekday = start_date.weekday()
    days_to_retreat = 1 + (this_weekday - weekday - 1) % 7
    retval = start_date + datetime.timedelta(days=-days_to_retreat)
    return retval


def first_weekday_of_month(date_in_month: datetime.date, weekday: int) -> datetime.date:
    if not (0 <= weekday <= 6):
        raise ValueError('weekday must be between 0 and 6')
    first_of_month = datetime.date(date_in_month.year, date_in_month.month, 1)
    first_weekday = first_of_month.weekday()
    days_to_advance = (weekday - first_weekday) % 7
    retval = first_of_month + datetime.timedelta(days=days_to_advance)
    return retval


def last_weekday_of_month(date_in_month: datetime.date, weekday: int) -> datetime.date:
    if not (0 <= weekday <= 6):
        raise ValueError('weekday must be between 0 and 6')
    last_of_month = last_date_of_month(date_in_month)
    last_weekday = last_of_month.weekday()
    days_to_retreat = (last_weekday - weekday) % 7
    retval = last_of_month + datetime.timedelta(days=-days_to_retreat)
    return retval
