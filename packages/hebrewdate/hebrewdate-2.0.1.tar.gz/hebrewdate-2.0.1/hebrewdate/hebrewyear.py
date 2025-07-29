"""
This module provides the HebrewYear class, which represents the Hebrew calendar year.

The class includes methods for determining if a year is a leap year, calculating the total
number of days in a year, computing the individual months and their lengths, and determining
the first weekday of the year. Additionally, it calculates the schedule of new moons and supports
operations such as year arithmetic and comparisons.
"""
#  Copyright (c) 2025 Isaac Dovolsky

from __future__ import annotations
import re

FIRST_NEW_MOON = 57444  # First new moon time in parts
NEW_MOON_INTERVAL = 765433  # Interval between new moons in parts
INVALID_FIRST_DAYS = {1, 4, 6}  # Invalid first days of the Hebrew year
LEAP_YEARS = {0, 3, 6, 8, 11, 14, 17}  # 0 instead of 19 due to modular calculation

# Standard and Leap Year Month Lengths
STANDARD_MONTHS = {
    "תשרי": 30, "חשוון": 29, "כסלו": 30, "טבת": 29, "שבט": 30, "אדר": 29,
    "ניסן": 30, "אייר": 29, "סיוון": 30, "תמוז": 29, "אב": 30, "אלול": 29
}
LEAP_MONTHS = {
    "תשרי": 30, "חשוון": 29, "כסלו": 30, "טבת": 29, "שבט": 30, "אדר א": 30,
    "אדר ב": 29, "ניסן": 30, "אייר": 29, "סיוון": 30, "תמוז": 29, "אב": 30,
    "אלול": 29
}

def _validate_year(year: int | str) -> int:
    if isinstance(year, str):
        year = HebrewYear.str_to_year(year)
    if year < 1 or year > 9999:
        raise ValueError(f"bad year value {year}")
    return year

class HebrewYear:
    """
    Represents a Hebrew year, handling leap years and calendar calculations.

    Attributes:
    -----------
    **year**: ``int``
        Numeric value of the Hebrew year.
    **year_str**: ``str``
        Traditional string representation of the Hebrew year.
    **is_leap**: ``bool``
        Whether the year is a leap year.
    **months**: ``list[str]``
        A list of month names for the year, adjusted for leap years.
    **days**: ``list[int]``
        Number of days in each month in the year.
    **month_count**: ``int``
        Number of months in the year (12 or 13 for leap years).
    **first_weekday**: ``int``
        Numeric representation of the year's first weekday (0-6, where 0 is שבת for calculation purposes).
    """

    def __init__(self, year: int | str):
        self.year = _validate_year(year)
        self.year_str = self.year_to_str(self.year)
        self.is_leap = self.is_leap_year(self.year)
        index = LEAP_MONTHS if self.is_leap else STANDARD_MONTHS
        self.months = list(index.keys())
        self.days = list(index.values())
        self.month_count = 13 if self.is_leap else 12
        self.first_weekday = self._first_weekday()
        self._calculate_days()

    def __repr__(self) -> str:
        return f"Year({self.year_str})"

    def __str__(self) -> str:
        return self.year_str

    def __int__(self) -> int:
        return self.year

    def __eq__(self, other: int | HebrewYear) -> bool:
        return self.year == int(other)

    def __ne__(self, other: int | HebrewYear) -> bool:
        return self.year != int(other)

    def __gt__(self, other: int | HebrewYear) -> bool:
        return self.year > int(other)

    def __lt__(self, other: int | HebrewYear) -> bool:
        return self.year < int(other)

    def __ge__(self, other: int | HebrewYear) -> bool:
        return self.year >= int(other)

    def __le__(self, other: int | HebrewYear) -> bool:
        return self.year <= int(other)

    def __len__(self) -> int:
        return self.month_count

    def __add__(self, other: int) -> HebrewYear:
        if isinstance(other, int):
            return HebrewYear(self.year + other)
        raise ValueError(f"Unsupported operand type(s) for +: 'Year' and {type(other).__name__}")

    def __sub__(self, other: int | HebrewYear) -> int | HebrewYear:
        if isinstance(other, int):
            return HebrewYear(self.year - other)
        if isinstance(other, HebrewYear):
            return self.year - other.year
        raise ValueError(f"Unsupported operand type(s) for -: 'Year' and {type(other).__name__}")

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return year % 19 in LEAP_YEARS

    def total_days(self) -> int:
        return sum(self.days)

    def month_dict(self) -> dict[str, int]:
        return dict(zip(self.months, self.days))

    def new_moons(self) -> dict[str, str]:
        """ Return a dictionary of new moons for each month. """
        first_new_moon = self.first_new_moon() % 181440  # 7 * 24 * 1080 = 181440
        return {
            self.months[month]: (
                f'{(month * NEW_MOON_INTERVAL + first_new_moon) // 1080 // 24 % 7}:'
                f'{(month * NEW_MOON_INTERVAL + first_new_moon) // 1080 % 24}:'
                f'{(month * NEW_MOON_INTERVAL + first_new_moon) % 1080}'
            )
            for month in range(self.month_count)
        }

    def first_new_moon(self, year: int = None) -> int:
        """ Returns the time of the year's first new moon (in parts) """
        year = (self.year if year is None else year) - 1
        # Number of leap years up to the current year
        leap_years = (year // 19) * 7 + sum(1 for j in LEAP_YEARS if j <= year % 19 and j != 0)
        # Total new moons up to the first new moon of the current year
        return (year * 12 + leap_years) * NEW_MOON_INTERVAL + FIRST_NEW_MOON

    def _first_weekday(self, year: int = None) -> int:
        """ Calculates the first weekday of the year. """
        year = self.year if year is None else year
        first_nm = self.first_new_moon(year)
        first_nmh = (first_nm // 1080) % 24
        first_day = (first_nm // 1080 // 24) % 7
        if first_day == 2 and self.is_leap_year(year - 1):
            if first_nmh == 15 and first_nm % 1080 >= 589 or first_nmh >= 16:
                first_day = 3
        elif first_day == 3 and not self.is_leap_year(year):
            if first_nmh == 9 and first_nm % 1080 >= 204 or first_nmh >= 10:
                first_day = 5
        elif first_nmh >= 18:
            first_day = (first_day + 1) % 7
        if first_day in INVALID_FIRST_DAYS:
            first_day = (first_day + 1) % 7
        return first_day

    def _calculate_days(self):
        """ Calculates the number of days in Heshvan and Kislev """
        if self.first_weekday != 3:
            next_theoretical = (self.total_days() + self.first_weekday) % 7
            next_actual = self._first_weekday(self.year + 1)
            if next_theoretical < next_actual or next_theoretical == 6 and next_actual == 0:
                self.days[1] = 30
            elif next_theoretical > next_actual or next_theoretical == 0 and next_actual == 1:
                self.days[1] = self.days[2] = 29

    @staticmethod
    def year_to_str(year: int) -> str:
        """
        Convert a numeric Hebrew year to its traditional Hebrew string representation.

        **year**: ``int``
            The numeric Hebrew year to convert (1-9999)
        """
        if year < 1 or year > 9999:
            raise ValueError(f"bad year value {year}")
        parts = []
        thousands, year = divmod(year, 1000)
        hundreds, year = divmod(year, 100)
        # Special case 400
        while hundreds >= 4:
            parts.append(chr(1514))  # ת
            hundreds -= 4
        # Hundreds
        if hundreds:
            parts.append(chr(1510 + hundreds))
        # Special cases for 15 and 16
        if year == 15:
            parts.extend(['ט', 'ו'])
        elif year == 16:
            parts.extend(['ט', 'ז'])
        else:
            tens, year = divmod(year, 10)
            # Tens
            if tens:
                tens = 1496 + tens + (tens // 2)
                parts.append(chr(tens + 1 if tens in (1503, 1509) else tens))
            # Units
            if year:
                parts.append(chr(1487 + year))
        # Add gershayim/geresh
        if len(parts) >= 2:
            parts[-2] += '"'  # Gershayim before last letter

        return (f"{chr(1487 + thousands)}'" if thousands else '') + ''.join(parts)
    
    @staticmethod
    def str_to_year(s: str) -> int:
        """
        Convert a Hebrew year string to its numeric value.

        **s**: ``str``
            The Hebrew year string to convert.

        Notes
        -----
        The valid formats for the year string are:

        - A geresh after the thousands part, e.g. ה'תשפה
        - A space after the thousands part, e.g. ה תשפה
        - Quotation marks before the units part, e.g. ה'תשפ"ה or ה תשפ"ה
        """
        pattern = re.compile(
            r"^(?P<th>[\u05d0-\u05d8][' ])?(?P<h>\u05ea{0,2}[\u05e7-\u05e9])?(?P<t>[\u05d8-\u05e6]?\"?[\u05d0-\u05d8]?)$"
        )
        if not (match := pattern.match(s)):
            raise ValueError(f"bad year value '{s}'")
        year = 0
        if match.group('th'):
            year += 1000 * (ord(match.group('th').replace("'", '').strip()) - 1487)
        if match.group('h'):
            year += sum(100 * (ord(char) - 1510) for char in match.group('h'))
        if match.group('t'):
            t = match.group('t').replace('"', '')
            if t == 'טו':
                year += 15
            elif t == 'טז':
                year += 16
            elif t[0] == 'ט':
                raise ValueError(f"bad year value '{s}'")
            elif ord(t[0]) > 1496:
                c = (ord(t[0]) - 1496) - (ord(t[0]) - 1496) // 3
                year += 10 * (c - 1 if c in {6, 10} else c)
                if len(t) > 1:
                    year += ord(t[1]) - 1487
            else:
                year += ord(t[0]) - 1487
        return year
