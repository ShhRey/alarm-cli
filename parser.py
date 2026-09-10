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


def parse_optional_args(args: List[str]) -> Dict[str, Any]:
    """
    Parse key-value CLI arguments supplied with the set command[cite: 3].
    Supports name, msg, snooze duration, and alarm type.
    """
    parsed: Dict[str, Any] = {
        "name": "Alarm",
        "message": "Alarm Triggered!",
        "snooze": 5,
        "alarm_type": AlarmType.ONCE,
    }

    for arg in args:
        if "=" not in arg:
            continue

        key, value = arg.split("=", 1)
        key = key.lower().strip()
        value = value.strip().strip('"')

        if key == "name":
            parsed["name"] = value

        elif key == "msg":
            parsed["message"] = value

        elif key == "snooze":
            try:
                snooze_minutes = int(value)
            except ValueError as exc:
                raise ValueError("Snooze duration must be an integer.") from exc

            if snooze_minutes <= 0:
                raise ValueError("Snooze duration must be greater than zero.")
            parsed["snooze"] = snooze_minutes

        elif key == "type":
            try:
                parsed["alarm_type"] = AlarmType(value.lower())
            except ValueError as exc:
                raise ValueError("Alarm type must be 'once' or 'daily'.") from exc

    return parsed