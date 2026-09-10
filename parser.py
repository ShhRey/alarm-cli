"""
Module: parser.py
Description: Robust parsing utilities for CLI command arguments and time strings.
             Handles date rollover logic for past times.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

from model import AlarmType


def parse_time_string(time_str: str) -> datetime | None:
    """
    Parse a 24-hour time string in HH:MM format.
    
    Senior Engineering Note: If the specified time has already elapsed today,
    automatically roll the target date over to tomorrow to prevent immediate firing.
    """
    try:
        parsed_time = datetime.strptime(time_str.strip(), "%H:%M")
    except ValueError:
        return None

    now = datetime.now()
    target_datetime = now.replace(
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=0,
        microsecond=0
    )

    # Automatically schedule for tomorrow if time has already passed today
    if target_datetime <= now:
        target_datetime += timedelta(days=1)

    return target_datetime
