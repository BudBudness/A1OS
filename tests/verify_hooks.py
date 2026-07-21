import inspect
from core.execution.v2.dispatcher.engine import DistributedDispatcher
from observability.monitoring.engine import MonitorEngine

def verify_class(cls, name):
    print(f"--- Verifying {name} ---")
    members = inspect.getmembers(cls, predicate=inspect.isfunction)
    for m in members:
        print(f"Hook found: {m[0]}")

if __name__ == "__main__":
    verify_class(DistributedDispatcher, "DistributedDispatcher")
    verify_class(MonitorEngine, "MonitorEngine")
