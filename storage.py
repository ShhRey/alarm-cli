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