
from enum import IntEnum

class Priority(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

class TaskPriority:
    def __init__(self, level: Priority):
        self.level = level

