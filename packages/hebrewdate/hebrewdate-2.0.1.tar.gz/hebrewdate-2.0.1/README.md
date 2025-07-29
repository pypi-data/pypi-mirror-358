# hebrewdate
A comprehensive Python library for working with the Hebrew calendar, providing date conversions, calendar generation, and holiday information.

It offers four main classes:

- ``HebrewDate``: Represents a specific date in the Hebrew calendar, with support for conversions
  to/from Gregorian dates, manipulation of dates (e.g., adding or subtracting days, months, or years),
  and various date-related attributes such as day, month, year, and weekday in the Hebrew calendar.
- ``HebrewYear``: Represents a Hebrew year, managing leap year calculations, month lengths, and
  determining the first weekday of the year.
- ``HebrewCalendar``: Extends Python's built-in `Calendar` class to provide Hebrew calendar functionality,
  including methods for iterating over month days and converting between Hebrew and Gregorian dates.
- ``HTMLHebrewCalendar``: Provides HTML formatting of Hebrew calendar data with support for both
  Hebrew and Gregorian date display, selection layers for holidays, festive days, and fasts, custom CSS styling.

#### Key Features:
- Conversion between Hebrew and Gregorian dates.
- Support for Hebrew holidays, festive days, and fasts.
- Computation of weekdays, month lengths, and leap years for Hebrew dates.
- Operations for date arithmetic, such as adding and subtracting days, months, and years.
- Methods for getting today's Hebrew date or constructing a Hebrew date from a Gregorian date.
- Calendar iteration and formatting for Hebrew dates in HTML format.
- Generate HTML calendars with customizable styling.
- Support for generating complete calendar pages for months and years.

#### Limitations:
- Supported Python versions: 3.9 and later
- Date conversions before 1752 CE may be inaccurate due to historical and calendar system variations.
- Dates far in the past may not be convertible to Gregorian dates

## Installation
```
pip install hebrewdate
``` 

## Usage
```
>>> from hebrewdate import HebrewDate, HTMLHebrewCalendar
# Get today's Hebrew date
>>> today = HebrewDate.today()
>>> print(today)
e.g. יום ראשון א ניסן ה'תשפ"ה
# Convert to Gregorian
>>> print(today.to_gregorian())
e.g. 2025-03-30

# Convert from Gregorian to Hebrew
>>> h = HebrewDate.from_gregorian(13, 4, 2025)
# Check holiday
>>> if h.is_holiday:
...     print(pesach.holiday)
...
יו"ט ראשון של פסח

# Generate an HTML calendar
cal = HTMLHebrewCalendar(with_gregorian=False)
html = cal.formatmonth(5785, 1) # תשרי ה'תשפ"ה
```

### Contribution

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Isaac Dovolsky © 2025