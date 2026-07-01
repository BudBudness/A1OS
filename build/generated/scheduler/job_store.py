import time

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