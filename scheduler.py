"""
Module: scheduler.py
Description: Background daemon thread evaluating active alarms against system time
             every second, handling triggers and daily rollovers safely.
"""

import threading
import time
from datetime import datetime, timedelta

from model import AlarmStatus, AlarmType
from service import AlarmService


class AlarmScheduler(threading.Thread):
    """
    Background worker thread monitoring scheduled alarm execution times.
    """

    def __init__(self, service: AlarmService) -> None:
        super().__init__(daemon=True)
        self.service = service
        self.running = True

    def stop(self) -> None:
        """Signal the background loop to terminate gracefully."""
        self.running = False

    def run(self) -> None:
        """Continuously check alarm triggers in a non-blocking background loop[cite: 4]."""
        while self.running:
            now = datetime.now()

            for alarm in self.service.list_alarms():
                if alarm.status != AlarmStatus.ACTIVE:
                    continue

                if alarm.time > now:
                    continue

                self._trigger_alarm(alarm)

            time.sleep(1)

    def _trigger_alarm(self, alarm) -> None:
        """Execute alarm notification and update recurrence state[cite: 4]."""
        print(f"\n⏰ ALARM TRIGGERED [{alarm.name}]: {alarm.message}")
        print("\a", end="", flush=True)  # System bell / beep

        if alarm.alarm_type == AlarmType.DAILY:
            # Advance daily alarm by 24 hours to prepare for tomorrow
            alarm.time += timedelta(days=1)
            alarm.status = AlarmStatus.ACTIVE
        else:
            alarm.status = AlarmStatus.TRIGGERED

        # Persist updated state to disk
        self.service.update_alarm_state(alarm)
        print("> ", end="", flush=True)  # Restore CLI prompt cursor