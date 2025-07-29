from enum import Enum


class IncidentGroupStatus(str, Enum):
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SILENCED = "silenced"
    TRIGGERED = "triggered"

    def __str__(self) -> str:
        return str(self.value)
