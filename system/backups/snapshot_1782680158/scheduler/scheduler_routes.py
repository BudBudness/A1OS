from api.router import SovereignAPIRouter
from scheduler.core import SovereignJobScheduler

scheduler = SovereignJobScheduler()

@SovereignAPIRouter.register_route("/scheduler/defer", method="POST")
def defer_job(body):
    if not body or "job" not in body or "delay" not in body:
        return 400, {"status": "ERROR", "message": "Missing job naming signature or execution delay string"}
    epoch = scheduler.defer_task(body["job"], float(body["delay"]))
    return 200, {"status": "QUEUED", "execution_epoch": epoch, "total_pending": len(scheduler.queue)}

@SovereignAPIRouter.register_route("/scheduler/jobs", method="GET")
def get_jobs(body):
    return 200, {"active_queue_frames": scheduler.queue}
