
from datetime import datetime


def get_current_datetime() -> dict:
    """
    Return the current date and time.

    Returns:
        A dictionary containing the date, time,
        and day of the week.
    """

    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M:%S %p"),
        "day": now.strftime("%A"),
    }
