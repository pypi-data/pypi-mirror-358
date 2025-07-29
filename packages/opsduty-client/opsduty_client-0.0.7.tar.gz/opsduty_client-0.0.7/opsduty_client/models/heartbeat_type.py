from enum import Enum


class HeartbeatType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"

    def __str__(self) -> str:
        return str(self.value)
