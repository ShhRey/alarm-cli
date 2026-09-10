"""
Module: storage.py
Description: Handles disk persistence for alarms using atomic JSON file I/O.
"""

import json
from pathlib import Path
from typing import List

from model import Alarm

STORAGE_FILE = Path("alarms.json")

def load_alarms() -> List[Alarm]:
    """
    Load and deserialize all stored alarms from disk.
    Returns an empty list if the storage file does not yet exist[cite: 6].
    """
    if not STORAGE_FILE.exists():
        return []

    try:
        with STORAGE_FILE.open("r", encoding="utf-8") as file:
            raw_alarms = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError("Alarm storage file contains corrupted JSON.") from exc

    if not isinstance(raw_alarms, list):
        raise ValueError("Alarm storage root must be a JSON array.")

    return [Alarm.from_dict(alarm) for alarm in raw_alarms]



def save_alarms(alarms: List[Alarm]) -> None:
    """
    Serialize and persist the current collection of alarms to disk[cite: 6].
    """
    serialized = [alarm.to_dict() for alarm in alarms]
    with STORAGE_FILE.open("w", encoding="utf-8") as file:
        json.dump(serialized, file, indent=2)