"""
This module provides Hebrew calendar functionality with both text and HTML representations.
It extends the built-in Calendar module to support Hebrew dates and formatting.
"""
#  Copyright (c) 2025 Isaac Dovolsky

import sys
from itertools import repeat
from .hebrewyear import HebrewYear
from calendar import Calendar, HTMLCalendar
from .hebrewdate import HebrewDate, _validate_month, WEEKDAYS, HEBREW_DAYS


class HebrewCalendar(Calendar):
    """
    A calendar class for working with Hebrew dates.
    
    This class extends the standard Calendar class to provide Hebrew calendar functionality,
    including methods for iterating over month days and converting between Hebrew and 
    Gregorian dates.
    
    Attributes:
    -----------
    **firstweekday**: ``int``
        Specifies the first day of the week (1 = Sunday, default)
    **with_gregorian**: ``bool``
        Specifies whether to include Gregorian dates in the calendar
    **with_holidays**: ``bool``
        Specifies whether to include holidays in the calendar
    **with_festive_days**: ``bool``
        Specifies whether to include festive days in the calendar
    **with_fasts**: ``bool``
        Specifies whether to include fasts in the calendar
    """

    def __init__(self, firstweekday: int = 1, with_gregorian: bool = True, with_holidays: bool = True,
                 with_festive_days: bool = False, with_fasts: bool = False):
        super().__init__(firstweekday)
        self.with_gregorian = with_gregorian
        self.with_holidays = with_holidays
        self.with_festive_days = with_festive_days
        self.with_fasts = with_fasts

    def itermonthdays(self, year, month):
        """
        Like itermonthdates(), but will yield day numbers. For days outside
        the specified month the day number is 0.
        """
        date = HebrewDate(month=month, year=year)
        day1, n_days = date.weekday_numeric, date.year.days[month - 1]
        days_before = (day1 - self.firstweekday) % 7
        yield from repeat(0, days_before)
        yield from range(1, n_days + 1)
        days_after = (self.firstweekday - day1 - n_days) % 7
        yield from repeat(0, days_after)

    def itermonthdays2(self, year, month):
        """
        Like itermonthdays(), but yields (day, weekday, gregorian_date, holiday) tuples.
        """
        for i, d in enumerate(self.itermonthdays(year, month), self.firstweekday):
            date = holiday = ""
            if d != 0:
                h_date = HebrewDate(d, month, year, self.with_festive_days, self.with_fasts)
                if self.with_gregorian:
                    try:
                        date = h_date.to_gregorian().strftime("%d")
                    except ValueError:
                        date = ""
                if self.with_holidays:
                    holiday = h_date.holiday
            yield d, i % 7, date, holiday


class HTMLHebrewCalendar(HebrewCalendar, HTMLCalendar):
    """
    HTML representation of the Hebrew calendar.
    
    This class combines HebrewCalendar and HTMLCalendar to provide HTML formatting
    of Hebrew calendar data. It supports both Hebrew and Gregorian date display,
    custom CSS styling, and various formatting options for days, weeks, months,
    and complete years.
    
    The calendar is formatted right-to-left (RTL) to match the Hebrew calendar structure
    and includes both Hebrew and optional Gregorian date representations.

    Attributes:
    -----------
    **custom_data**: ``dict``
        A dictionary that allows adding custom styling and content to specific days
        in the calendar. The dictionary should use day numbers as keys (1-31),
        and each value should be a dictionary containing:
        - 'classes': list of CSS class names to add to the day's cell
        - 'content': list of HTML strings to append after the date content

        Example:

        >>> custom_data = {
        ...    15: {
        ...        'classes': ['highlight', 'special-day'],
        ...        'content': ['<div class="event">Meeting</div>']
        ...    }
        ... }
    **firstweekday**: ``int``
        Specifies the first day of the week (1 = Sunday, default)
    **with_gregorian**: ``bool``
        Specifies whether to include Gregorian dates in the calendar
    **with_holidays**: ``bool``
        Specifies whether to include holidays in the calendar
    **with_festive_days**: ``bool``
        Specifies whether to include festive days in the calendar
    **with_fasts**: ``bool``
        Specifies whether to include fasts in the calendar
    """
    def __init__(self, custom_data: dict = None, firstweekday=1, with_gregorian=True, with_holidays=True,
                 with_festive_days=False, with_fasts=False):
        HebrewCalendar.__init__(self, firstweekday, with_gregorian, with_holidays, with_festive_days, with_fasts)
        HTMLCalendar.__init__(self, firstweekday)
        self.custom_data = custom_data or {}

    def formatday(self, day, weekday, *args):
        """
        Return a day as a table cell with support for custom data and styling.

        Parameters:
        -----------
        **day**: ``int``
            Day number (0 for days outside the month)
        **weekday**: ``int``
            Day of week (0-6)
        **args**:
            Additional content to add to the cell (e.g., Gregorian date, holiday)

        The method checks self.custom_data for additional formatting:

        * If self.custom_data is present, it should be a dict with day numbers as keys
        * Each value should be a dict containing:
            - 'classes': list of additional CSS classes
            - 'content': list of HTML content to append after the date
        """
        if day == 0:
            return f'<td class="{self.cssclass_noday}">&nbsp;</td>'

        # Initialize classes and content
        classes = [self.cssclasses[weekday], 'day']
        content = [f'<div class="date-content">{HEBREW_DAYS[day - 1]}']
        # Add standard data (Gregorian dates and holidays)
        for c in args:
            if c:
                content.append(f'<br>{c}')
        content.append('</div>')
        # Add custom data if present
        if self.custom_data and day in self.custom_data:
            day_data = self.custom_data[day]
            if 'classes' in day_data:
                classes.extend(day_data['classes'])
            if 'content' in day_data:
                content.extend(day_data['content'])
        classes_str = ' '.join(classes)
        content_str = ''.join(content)
        return f'<td class="{classes_str}" data-date="{day}">{content_str}</td>'

    def formatweek(self, week):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, g, h) for (d, wd, g, h) in week)
        return f'<tr>{s}</tr>'

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return f'<th class="weekday {self.cssclasses_weekday_head[day]}">{WEEKDAYS[day]}</th>'

    def formatmonthname(self, year, month, with_year=True):
        """
        Return a month name as a table row.
        """
        _validate_month(month, year)
        h_year = HebrewYear(year)
        if self.with_gregorian:
            start = HebrewDate(month=month, year=year)
            end = (start + h_year.days[month - 1]).to_gregorian().strftime("%B")
            start = start.to_gregorian()
            g_year = start.year
            start = start.strftime('%B')
            gm = f'{start}-{end}' if start != end else start
            if with_year:
                s = f'{h_year.months[month - 1]} {h_year}\n{gm} {g_year}'
            else:
                s = f'{h_year.months[month - 1]}\n{gm}'
        else:
            if with_year:
                s = f'{h_year.months[month - 1]} {h_year}'
            else:
                s = h_year.months[month - 1]
        return f'<thead><tr><th colspan="7" class="{self.cssclass_month_head}">{s}</th></tr></thead>'

    def formatmonth(self, year, month, with_year=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a(f'<table dir="rtl" border="0" cellpadding="0" cellspacing="0" class="{self.cssclass_month}">')
        a('\n')
        a(self.formatmonthname(year, month, with_year))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(year, month):
            a(self.formatweek(week))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatyear(self, year, width=3):
        """
        Return a formatted year as a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        h_year = HebrewYear(year)
        a(f'<table dir="rtl" border="0" cellpadding="0" cellspacing="0" class="{self.cssclass_year}">')
        a('\n')
        a(f'<thead><tr><th colspan="{width}" class="{self.cssclass_year_head}">{h_year}</th></tr></thead>')
        for i in range(1, h_year.month_count + 1, width):
            # months in this row
            months = range(i, min(i + width, 14))
            a('<tr>')
            for m in months:
                a('<td>')
                a(self.formatmonth(year, m, False))
                a('</td>')
            a('</tr>')
        a('</table>')
        return ''.join(v)

    def formatyearpage(self, year, width=3, css="calendar.css", encoding=None):
        """
        Return a formatted year as a complete HTML page.
        """
        if encoding is None:
            encoding = sys.getdefaultencoding()
        v = []
        a = v.append
        a(f'<?xml version="1.0" encoding="{encoding}"?>\n')
        a('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')
        a('<html>\n')
        a('<head>\n')
        a(f'<meta http-equiv="Content-Type" content="text/html; charset={encoding}" />\n')
        if css is not None:
            a(f'<link rel="stylesheet" type="text/css" href="{css}" />\n')
        a(f'<title>Calendar for {HebrewYear.year_to_str(year)}</title>\n')
        a('</head>\n')
        a('<body>\n')
        a(self.formatyear(year, width))
        a('</body>\n')
        a('</html>\n')
        return ''.join(v).encode(encoding, "xmlcharrefreplace")
