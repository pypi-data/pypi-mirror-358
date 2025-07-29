"""
This module contains information about Hebrew holidays, festive days and fasting days.
"""
#  Copyright (c) 2025 Isaac Dovolsky

HOLIDAYS = {
    'תשרי': {
        'ראש השנה': (1, 2),
        'יום כיפור': 10,
        'יו"ט ראשון של סוכות': 15,
        'שמחת תורה': 22,
    },
    'ניסן': {
        'יו"ט ראשון של פסח': 15,
        'שביעי של פסח': 21
    },
    'סיוון': {
        'שבועות': 6
    }
}
FESTIVE_DAYS = {
    'תשרי': {
        'חול המועד סוכות': (16, 17, 18, 19, 20),
        'הושענא רבה': 21
    },
    'כסלו': {
        'חנוכה': (25, 26, 27, 28, 29, 30)
    },
    'טבת': {
        'חנוכה': (1, 2, 3)
    },
    'אדר': {
        'פורים': 14,
        'שושן פורים': 15,
        'שושן פורים משולש': 16
    },
    'ניסן': {
        'חול המועד פסח': (16, 17, 18, 19, 20)
    },
    'אייר': {
        'ל"ג בעומר': 18
    }
}
FASTS = {
    'תשרי': {
        'צום גדליה': 3
    },
    'טבת': {
        'צום עשרה בטבת': 10
    },
    'אדר': {
        'תענית אסתר': 13
    },
    'תמוז': {
        'צום י"ז בתמוז': 17
    },
    'אב': {
        'צום תשעה באב': 9
    }
}
FESTIVE_DAYS['אדר ב'] = FESTIVE_DAYS['אדר']
FASTS['אדר ב'] = FASTS['אדר']

def get_holiday(date, include_festive_days: bool = False, include_fasts: bool = False) -> tuple[bool, str]:
    """
    Check if the given Hebrew date is a holiday.

    Args:
        date: HebrewDate object to check
        include_festive_days: Whether to include festive days like Chol HaMoed
        include_fasts: Whether to include fasting days

    Returns:
        tuple[True, holiday name] if the date is a holiday, False otherwise
    """
    # Check main holidays
    if date.month in HOLIDAYS:
        for holiday, day in HOLIDAYS[date.month].items():
            if isinstance(day, tuple):
                if date.day_numeric in day:
                    return True, holiday
            elif date.day_numeric == day:
                return True, holiday
    if include_festive_days:
        if date.month in FESTIVE_DAYS:
            if date.month == 'טבת' and date.year.month_dict()['כסלו'] == 30 and date.day_numeric == 3:
                return False, ''
            if 'אדר' in date.month and date.day_numeric == 16 and date.weekday_numeric != 1:
                return False, ''
            for festive, day in FESTIVE_DAYS[date.month].items():
                if isinstance(day, (tuple, set)):
                    if date.day_numeric in day:
                        return True, festive
                elif date.day_numeric == day:
                    return True, festive
    if include_fasts:
        if date.month in FASTS:
            if 'אדר' in date.month:
                if date.day_numeric == 13 and date.weekday_numeric == 7:
                    return False, ''
                elif date.day_numeric == 11 and date.weekday_numeric == 5:
                    date.day_numeric = 13
            for fast, day in FASTS[date.month].items():
                if isinstance(day, tuple):
                    if date.day_numeric in day:
                        return True, fast
                elif date.day_numeric == day:
                    return True, fast
    return False, ''
