from dataclasses import dataclass
from datetime import datetime

@dataclass
class Alarm:
    time: datetime
    message: str
    active: bool = True