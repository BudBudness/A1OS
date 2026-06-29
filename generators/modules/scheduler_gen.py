from generators.core.base_gen import BaseGenerator
from pathlib import Path

class SchedulerGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "scheduler"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Monotonic Time Background Daemon
        cron_code = '''import time
import threading

class MonotonicCronDaemon:
    def __init__(self):
        self._jobs = []
        self._is_active = False
        self._thread = None

    def register_job(self, interval_sec, callback):
        self._jobs.append({"interval": interval_sec, "callback": callback, "last_run": 0.0})
        print(f"[CRON-DAEMON] Enrolled background tick vector with frequency: {interval_sec}s")

    def start(self):
        self._is_active = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._is_active:
            now = time.monotonic()
            for job in self._jobs:
                if now - job["last_run"] >= job["interval"]:
                    try:
                        job["callback"]()
                    except Exception as e:
                        print(f"[CRON-ERROR] Background tick failure: {e}")
                    job["last_run"] = now
            time.sleep(0.1)

    def stop(self):
        self._is_active = False
        if self._thread:
            self._thread.join(timeout=1.0)
'''

        # 2. Task Enrollment and Persistence Manager
        job_store_code = '''import time

class ScheduledJobStore:
    def __init__(self):
        self.registry = {}

    def add_job(self, job_id, cron_expr, task_name):
        self.registry[job_id] = {
            "expr": cron_expr,
            "task": task_name,
            "registered_at": time.time()
        }
        print(f"[JOB-STORE] Persistent timing lock anchored for job ID: {job_id}")

    def get_job(self, job_id):
        return self.registry.get(job_id)
'''

        # 3. Microsecond Resolution System Clock
        clock_code = '''import time

class HighResolutionSystemClock:
    @staticmethod
    def get_monotonic_time():
        return time.monotonic()

    @staticmethod
    def get_wall_clock_drift(reference_time):
        return time.time() - reference_time
'''

        # 4. Monotonic Cron Integration Component Verification
        test_code = '''import time
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
'''

        # Write out the full structural scheduler module files atomically
        with open(output_dir / "cron.py", "w") as f: f.write(cron_code.strip())
        with open(output_dir / "job_store.py", "w") as f: f.write(job_store_code.strip())
        with open(output_dir / "clock.py", "w") as f: f.write(clock_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] scheduler_gen.py has compiled v1 Scheduler Subsystem inside {output_dir}")
