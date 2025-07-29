"""
This module provides functionality for working with Hebrew dates.
It enables the representation of Hebrew dates, conversions between Hebrew and Gregorian calendars, 
and various date arithmetic operations.
"""
#  Copyright (c) 2025 Isaac Dovolsky

from __future__ import annotations
import warnings
import datetime as dt
from .holidays import get_holiday
from .hebrewyear import HebrewYear

EPOCH_H_DATE = (14, 4, 5512)  # Hebrew date of Gregorian Epoch (14 Nissan 5512)
EPOCH_G_DATE = (1752, 1, 1)  # Corresponding Gregorian Epoch

# Hebrew Days and Weekdays
HEBREW_DAYS = (
    "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "יא", "יב", "יג", "יד",
    "טו", "טז", "יז", "יח", "יט", "כ", "כא", "כב", "כג", "כד", "כה", "כו", "כז",
    "כח", "כט", "ל"
)
WEEKDAYS = ("שבת", "ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי")

def _validate_month(month: int | str, year: int) -> str:
    year = HebrewYear(year)
    if isinstance(month, int):
        if month < 1 or month > (13 if year.is_leap else 12):
            raise ValueError(f"bad month value '{month}'")
        month = year.months[month - 1]
    elif isinstance(month, str):
        if month not in year.months:
            raise ValueError(f"bad month value '{month}'")
    else:
        raise TypeError("Invalid month type")
    return month

def _validate_day(day: int | str, month: int, year: int) -> str:
    year = HebrewYear(year)
    if isinstance(day, int):
        if day < 1 or day > year.days[month - 1]:
            raise ValueError(f"bad day value '{day}' for {year.days[month - 1]}-day month")
        day = HEBREW_DAYS[day - 1]
    elif isinstance(day, str):
        day = day.replace('"', '')
        if day not in HEBREW_DAYS:
            raise ValueError(f"bad day value '{day}'")
    else:
        raise TypeError("Invalid day type")
    return day


class HebrewDate:
    """
    Represents a Hebrew date, supporting conversions, arithmetic.

    Parameters:
    -----------
    **day**: ``int`` | ``str``, optional (default: 1)
        The day of the Hebrew date, represented either as an integer (1-30) or as a string (see notes below).
    **month**: ``int`` | ``str``, optional (default: 1)
        The month of the Hebrew date, represented either as an integer (1-12/13) or as a string.
    **year**: ``int`` | ``str``, optional (default: 5785)
        The year of the Hebrew date, represented either as an integer (1-9999) or as a string (see notes below).
    **include_festive_days**: ``bool``, optional (default: False)
        Specifies whether to include festive days in the calculation of holidays.
    **include_fasts**: ``bool``, optional (default: False)
        Specifies whether to include fasts in the calculation of holidays.

    Attributes:
    -----------
    **year**: ``HebrewYear``
        ``HebrewYear`` object representing the year of the Hebrew date.
    **year_numeric**: ``int``
        Numeric value of the Hebrew year.
    **month**: ``str``
        Name of the Hebrew month.
    **month_numeric**: ``int``
        Numeric value of the Hebrew month (1-12/13).
    **day**: ``str``
        Day of the Hebrew date as a Hebrew string representation.
    **day_numeric**: ``int``
        Numeric day of the month (1-30).
    **weekday**: ``str``
        Hebrew name of the weekday.
    **weekday_numeric**: ``int``
        Numeric representation of the Hebrew weekday (1-7, where 1 is Sunday).
    **genesis**: ``int``
        The number of parts since the Hebrew epoch up to the start of the current date.
    **is_holiday**: ``bool``
        Specifies whether the current date is a Hebrew holiday.
    **holiday**: ``str``
        The holiday name if the current date is a Hebrew holiday, otherwise ''.

    Notes:
    ------
    The string input for the day parameter can be both with quotation marks in the middle or without.

    The valid input formats for the year parameter as a string are as follows:

    - A geresh after the thousands part, e.g. ה'תשפה
    - A space after the thousands part, e.g. ה תשפה
    - Quotation marks before the units part, e.g. ה'תשפ"ה or ה תשפ"ה
    """

    def __init__(self, day: int | str = 1, month: int | str = 1, year: int | str = 5785,
                 include_festive_days: bool = False, include_fasts: bool = False):
        self.year = HebrewYear(year)
        self.year_numeric = self.year.year
        self.month = _validate_month(month, self.year_numeric)
        self.month_numeric, self.month = self.get_month()
        self.day = _validate_day(day, self.month_numeric, self.year_numeric)
        self.day_numeric, self.day = self.get_day()
        self.weekday_numeric, self.weekday = self.get_weekday()
        self.genesis = self.year.first_new_moon() + self.days_before() * 1080 * 24
        self.is_holiday, self.holiday = get_holiday(self, include_festive_days, include_fasts)

    def __repr__(self) -> str:
        return f"HebrewDate({self.__str__()})"

    def __str__(self) -> str:
        return f"יום {self.weekday} {self.day} {self.month} {self.year}"

    def __int__(self) -> int:
        return self.genesis

    def __eq__(self, other: int | float | HebrewDate) -> bool:
        return int(self) == int(other)

    def __ne__(self, other: int | float | HebrewDate) -> bool:
        return int(self) != int(other)

    def __lt__(self, other: int | float | HebrewDate) -> bool:
        return int(self) < int(other)

    def __gt__(self, other: int | float | HebrewDate) -> bool:
        return int(self) > int(other)

    def __le__(self, other: int | float | HebrewDate) -> bool:
        return int(self) <= int(other)

    def __ge__(self, other: int | float | HebrewDate) -> bool:
        return int(self) >= int(other)

    def __add__(self, other: int | float) -> HebrewDate:
        if isinstance(other, (int, float)):
            return self.delta(days=int(other))
        raise ValueError(f"Unsupported operand type(s) for +: 'HebrewDate' and {type(other).__name__}")

    def __sub__(self, other: int | float | HebrewDate) -> int | HebrewDate:
        if isinstance(other, (int, float)):
            return self.delta(days=-int(other))
        if isinstance(other, HebrewDate):
            return (int(self) - int(other)) // 1080 // 24
        raise TypeError(f"Unsupported operand type(s) for +: 'HebrewDate' and {type(other).__name__}")

    def get_month(self) -> tuple[int, str]:
        """Get the month number and name as a tuple."""
        return self.year.months.index(self.month) + 1, self.month

    def get_day(self) -> tuple[int, str]:
        """Get the day number and name as a tuple."""
        return HEBREW_DAYS.index(self.day) + 1, self.day

    def get_weekday(self) -> tuple[int, str]:
        """Get the weekday number and name as a tuple."""
        weekday = (sum(i for i in self.year.days[:self.month_numeric - 1]) +
                   self.year.first_weekday + self.day_numeric - 1) % 7
        return (7 if weekday == 0 else weekday), WEEKDAYS[weekday]

    def days_before(self) -> int:
        """Calculates the number of days from the start of the year to the current date."""
        if self.month_numeric == 1:
            return self.day_numeric - 1
        return sum(self.year.days[:self.month_numeric - 1]) + self.day_numeric - 1

    def days_after(self) -> int:
        """Calculates the number of days from the current date till the end of the year."""
        return sum(self.year.days[self.month_numeric:]) + self.year.days[self.month_numeric - 1] - self.day_numeric

    # noinspection PyUnresolvedReferences
    def delta(self, days: int = 0, months: int = 0, years: int = 0) -> HebrewDate:
        """
        Computes a new HebrewDate instance by an offset of the given days, months, and years.
        """
        # Adjust the Year
        new_year = HebrewYear(self.year_numeric + years)

        # Adjust the Month
        new_month = self.month_numeric - 1 + months  # Convert to 0-based index
        while new_month < 0:  # Handle underflow
            new_year -= 1
            new_month += new_year.month_count
        while new_month >= new_year.month_count:  # Handle overflow
            new_month -= new_year.month_count
            new_year += 1

        # Adjust the Day
        new_day = self.day_numeric + days
        while new_day < 1:  # Handle day underflow
            new_month -= 1
            if new_month < 0:
                new_year -= 1
                new_month = new_year.month_count - 1
            new_day += new_year.days[new_month]
        while new_day > new_year.days[new_month]:  # Handle day overflow
            new_day -= new_year.days[new_month]
            new_month += 1
            if new_month >= new_year.month_count:
                new_year += 1
                new_month = 0
        return HebrewDate(day=new_day, month=new_month + 1, year=new_year.year)

    @classmethod
    def from_gregorian(cls, day: int = None, month: int = None, year: int = None, date: dt.date = None) -> HebrewDate:
        """
        Creates a HebrewDate object from a Gregorian date.

        Parameters:
        -----------
        **day**: ``int``, optional
            The day of the Gregorian date.
        **month**: ``int``, optional
            The month of the Gregorian date.
        **year**: ``int``, optional
            The year of the Gregorian date.
        **date**: ``datetime.date``, optional
            A datetime.date object representing the Gregorian date.

        Returns:
        --------
        ``HebrewDate``
            A corresponding HebrewDate object.

        Raises:
        -------
        ``TypeError``
            If `date` is provided but is not a datetime.date object.
        ``ValueError``
            If both `date` and the `day`, `month`, and `year` arguments are missing.
        """
        if date is not None:
            if not isinstance(date, dt.date):
                raise TypeError("date must be a datetime.date object")
        elif day and month and year:
            date = dt.date(year, month, day)
        else:
            raise ValueError("Provide either a valid `date` or `day`, `month`, and `year` arguments.")
        if date.year < 1752:
            warnings.warn("Hebrew dates may be inaccurate for years earlier than 1752.", RuntimeWarning, 2)
        return cls(*EPOCH_H_DATE) + (date - dt.date(*EPOCH_G_DATE)).days

    def to_gregorian(self) -> dt.date | None:
        """
        Converts the current HebrewDate object to a Gregorian date.

        Returns:
        --------
        ``datetime.date`` | ``None``
            The corresponding Gregorian date, or None if the conversion is not possible.
        """
        try:
            date = dt.date(*EPOCH_G_DATE) + dt.timedelta(days=(self - HebrewDate(*EPOCH_H_DATE)) + 1)
            if date.year < 1752:
                warnings.warn(
                    "Hebrew dates may be inaccurate for years earlier than 1752.", RuntimeWarning, 2)
            return date
        except OverflowError:
            warnings.warn(
                "The Hebrew date is too far in the past to convert to a Gregorian date.", RuntimeWarning, 2)
            return None

    @classmethod
    def today(cls) -> HebrewDate:
        """ Returns the current Hebrew date. """
        return cls.from_gregorian(date=dt.date.today())
