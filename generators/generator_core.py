# generator_core.py - Folder Registry Configuration
import os
BASE_DIR = os.path.expanduser("~/A1OS")
REGISTRY = {
    "memory": os.path.join(BASE_DIR, "memory/context"),
    "tasks": os.path.join(BASE_DIR, "tasks/queue"),
    "agents": os.path.join(BASE_DIR, "agents/active"),
    "events": os.path.join(BASE_DIR, "events/triggers")
}
def init_system():
    for path in REGISTRY.values():
        os.makedirs(path, exist_ok=True)
