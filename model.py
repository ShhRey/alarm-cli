"""
Module: model.py
Description: Defines core data structures, types, and serialization schemas
             for alarms, supporting both one-time and recurring schedules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AlarmType(Enum):
    """Defines recurrence rules for the alarm."""
    ONCE = "once"
    DAILY = "daily"


class AlarmStatus(Enum):
    """Current lifecycle state of an alarm instance."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    SNOOZED = "snoozed"
    CANCELLED = "cancelled"
