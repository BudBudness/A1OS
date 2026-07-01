import time
from .cron import MonotonicCronDaemon
from .job_store import ScheduledJobStore
from .clock import HighResolutionSystemClock

def test_scheduler_subsystem():
    daemon = MonotonicCronDaemon()
    store = ScheduledJobStore()
    
    # 1. Validate Job Persistence Storage
    store.add_job("sync_01", "*/5 * * * *", "TELEMETRY_SYNC")
    assert store.get_job("sync_01")["task"] == "TELEMETRY_SYNC"
    
    # 2. Validate Monotonic Cron Ticking
    counter = [0]
    daemon.register_job(0.2, lambda: counter.__setitem__(0, counter[0] + 1))
    daemon.start()
    
    time.sleep(0.5)
    daemon.stop()
    assert counter[0] >= 1
    
    # 3. High-resolution monotonic system check
    assert HighResolutionSystemClock.get_monotonic_time() > 0
    
    print("✅ Monotonic Cron Scheduler Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_scheduler_subsystem()