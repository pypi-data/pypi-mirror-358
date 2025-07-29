# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 27-06-2025

### Added

- Added support for Hebrew holidays, festive days, and fasting days
- Enhanced HTML calendar formatting with holidays
- Improved CSS customization options
- Traditional string representation for Hebrew years
- Improved documentation

### Changes

- `HebrewDate` and `HebrewYear` accept a formatted string for the year argument (see formats in docs)
- `HebrewDate.genesis` represents the number of **parts** since the epoch instead of days
- refactored the `with_gregorian` argument from the formatting methods of `HebrewCalendar` and `HTMLHebrewCalendar`,
  to an attribute of these classes, which can be passed upon initialization or set later.
- renamed `HebrewCalendar.itermonthdays2gregorian` to `HebrewCalendar.itermonthdays2`
- `HebrewCalendar.itermonthdays2` always yields Gregorian dates and holiday strings
  (in addition to the default day and weekday). If the corresponding flags are set to False, 
  then they are guaranteed to be empty strings.
- `HTMLHebrewCalendar.format_day` accepts additional non-keyword arguments to insert into its element

### Fixed

- Incorrect subtraction between `HebrewDate` instances
- `HebrewCalendar` didn't account for old dates, which cannot have a Gregorian date


### Removed

- Removed support for Python version 3.8
- `IllegalMonthError` and `IllegalWeekdayError`. Using standard `ValueError` instead.

## [1.0.0] - 29-04-2025

### Added

- Conversion between Hebrew and Gregorian dates.
- Computation of weekdays, month lengths, and leap years for Hebrew dates.
- Operations for date arithmetic, such as adding and subtracting days, months, and years.
- Methods for getting today's Hebrew date or constructing a Hebrew date from a Gregorian date.
- Calendar iteration and formatting for Hebrew dates in HTML format.
- Right-to-left (RTL) HTML calendar display with optional Gregorian date annotations.
- Customizable CSS styling for calendar presentation.
- Support for generating complete calendar pages for months and years.
