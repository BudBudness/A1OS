import time
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