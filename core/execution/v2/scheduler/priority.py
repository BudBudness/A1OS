
from dataclasses import dataclass
from enum import IntEnum

class Priority(IntEnum):
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class TaskPriority:
    level: Priority
    weight: float
    deadline: float = 0.0

