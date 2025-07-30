from datetime import datetime, timezone
from persiantools.jdatetime import JalaliDate


def create_datetime(dt_text: str) -> datetime:
    """Creates a datetime for datetime formats found in iranintl articles and livepages.

    2025-06-27T17:13:30.894Z"""
    # Remove trailing 'Z' and parse timezone as UTC
    dt_text = dt_text.rstrip("Z")
    try:
        # Try parsing with fractional seconds
        dt = datetime.strptime(dt_text, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        # Fallback: parse without fractional seconds
        dt = datetime.strptime(dt_text, "%Y-%m-%dT%H:%M:%S")
    # Set UTC timezone
    dt = dt.replace(tzinfo=timezone.utc)
    return dt


def persian_date_to_datetime(persian_date_str: str):
    """
    Convert a Persian date string like 'جمعه ۱۴۰۴/۴/۶' to a datetime object.

    Args:
        persian_date_str (str): Persian date string in format 'DAYOFWEEK YYYY/MM/DD'

    Returns:
        datetime.datetime: Corresponding Gregorian datetime object
    """
    # Split the string by space to separate day of week and date
    parts = persian_date_str.split()
    if len(parts) != 2:
        raise ValueError("Input format must be 'DAYOFWEEK YYYY/MM/DD'")

    # Extract the date part (e.g. '۱۴۰۴/۴/۶')
    persian_date = parts[1]

    # Persian digits to English digits mapping
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"

    # Function to convert Persian numerals to English numerals
    def convert_persian_digits(persian_num_str):
        for p, e in zip(persian_digits, english_digits):
            persian_num_str = persian_num_str.replace(p, e)
        return persian_num_str

    persian_date_english = convert_persian_digits(persian_date)

    # Parse year, month, day
    year_str, month_str, day_str = persian_date_english.split("/")
    year, month, day = int(year_str), int(month_str), int(day_str)

    # Convert Jalali date to Gregorian date
    gregorian_date = JalaliDate(year, month, day).to_gregorian()

    # Return as datetime object (at midnight)
    return datetime(gregorian_date.year, gregorian_date.month, gregorian_date.day)
