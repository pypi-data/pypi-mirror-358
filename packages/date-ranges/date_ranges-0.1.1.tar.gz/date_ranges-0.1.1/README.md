# date-ranges

A `DateRange` type and related utility functions.

## Quickstart

Install from pip:

```shell
pip install date-ranges
```

Import and create an instance:
```python
from datetime import date

from date_ranges import DateRange

my_date_range = DateRange(start=date(2023, 5, 10), end=date(2023, 11, 3))
```

## Usage

```python
from datetime import date

from date_ranges import DateRange, MAX_DATE

# end date defaults to MAX_DATE
dr = DateRange(date(2023, 11, 1))

date(2023, 11, 22) in dr
# True

# An empty date (0 days in range):
empty = DateRange.empty()
bool(empty)
# False

# Iteration
for d in DateRange(date(2023, 1, 1), date(2023, 1, 3)):
    print(d)
# 2023-01-01
# 2023-01-02
# 2023-01-03

# Create from strings
dr = DateRange.from_string('20230101-20230103')
repr(dr)
# 'DateRange(start=datetime.date(2023, 1, 1), end=datetime.date(2023, 1, 3))'

# Create range for a single date
dr = DateRange.from_string('20231031')
repr(dr)
# 'DateRange(start=datetime.date(2023, 10, 31), end=datetime.date(2023, 10, 31))'

# Create range for given year-month
dr = DateRange.from_string('202305')
repr(dr)
# 'DateRange(start=datetime.date(2023, 5, 1), end=datetime.date(2023, 5, 31))'

# Create range for multiple full months
dr = DateRange.from_string('202305-202311')
repr(dr)
# 'DateRange(start=datetime.date(2023, 5, 1), end=datetime.date(2023, 11, 30))'

# Formatted print
dr = DateRange(date(2023, 1, 1), date(2023, 1, 3))
dr
# 20230101-20230103
print(f'{dr:H}')   # H for human
# 2023-01-01 to 2023-01-03

# Full months rendered appropriately
dr = DateRange.from_string('202305')
f'{dr:H}'  # H for "human-readable"
# 'May 2023'
f'{dr:C}'  # C for compact
# '202305'
dr
# '202305'
```


## Development

For those developing or maintaining the `date-ranges` package itself,
be sure to install it with the `[dev]` option to pull in packages
used when developing.

    pip install --editable .[dev]

When developing, this package uses `pre-commit`.  After the initial
clone of the repository, you will need to set up pre-commit with:

    # in the top level of the checked-out repository:
    pre-commit install

## Changelog

### 0.1.1 released 2025-06-27
* Fixed explicit exports

### 0.1.0 released 2025-06-26
* Add utility functions
  * weekday_after, weekday_before, first_weekday_of_month, last_weekday_of_month

### 0.0.2 released 2023-11-10
* Fixed typo

### 0.0.1 released 2023-11-03
* Initial Version
