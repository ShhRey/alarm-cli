import threading
from datetime import datetime, timedelta
from typing import List

from model import Alarm, AlarmStatus, AlarmType
from storage import load_alarms, save_alarms

class AlarmService:
    """
    Thread-safe service layer encapsulating all alarm business operations.
    """


    def set_alarm(
        self,
        alarm_time: datetime,
        name: str,
        message: str,
        snooze_minutes: int,
        alarm_type: AlarmType = AlarmType.ONCE,
    ) -> Alarm:
        """Create, persist, and register a new alarm."""
        with self._lock:
            if snooze_minutes <= 0:
                raise ValueError("Snooze duration must be greater than zero.")

            alarm = Alarm(
                time=alarm_time,
                name=name,
                message=message,
                alarm_type=alarm_type,
                snooze_minutes=snooze_minutes,
            )

            self.alarms.append(alarm)
            save_alarms(self.alarms)
            return alarm