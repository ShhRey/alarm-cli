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



@dataclass
class Alarm:
    """
    Core domain model representing an alarm.
    Maintains timing, metadata, and persistence mapping.
    """
    time: datetime
    name: str
    message: str
    alarm_type: AlarmType = AlarmType.ONCE
    snooze_minutes: int = 5
    status: AlarmStatus = AlarmStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize domain model into a JSON-compatible dictionary[cite: 2]."""
        return {
            "time": self.time.isoformat(),
            "name": self.name,
            "message": self.message,
            "alarm_type": self.alarm_type.value,
            "snooze_minutes": self.snooze_minutes,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Alarm":
        """Deserialize a dictionary back into a strongly typed Alarm instance[cite: 2]."""
        return cls(
            time=datetime.fromisoformat(data["time"]),
            name=data["name"],
            message=data["message"],
            alarm_type=AlarmType(data.get("alarm_type", AlarmType.ONCE.value)),
            snooze_minutes=data.get("snooze_minutes", 5),
            status=AlarmStatus(data.get("status", AlarmStatus.ACTIVE.value)),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )