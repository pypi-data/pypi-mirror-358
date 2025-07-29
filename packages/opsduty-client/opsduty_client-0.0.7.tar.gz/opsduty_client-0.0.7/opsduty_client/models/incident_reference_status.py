from enum import Enum


class IncidentReferenceStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    STOPPED = "stopped"

    def __str__(self) -> str:
        return str(self.value)
