import os, time, json, logging
BASE = "/data/data/com.termux/files/home/A1OS"
PENDING, ACTIVE, LOG = os.path.join(BASE, "data/tasks/pending"), os.path.join(BASE, "data/tasks/active"), os.path.join(BASE, "logs/ops/daemon.log")
logging.basicConfig(filename=LOG, level=logging.INFO, format='%(asctime)s - %(message)s')
def handle_ping(data): logging.info(f"Ping received: {data.get('id')}")
def handle_backup(data): logging.info(f"Backup triggered for: {data.get('target', 'all')}")
def handle_cleanup(data): logging.info("System cleanup initiated.")
def handle_status(data):
    r_path = os.path.join(BASE, "data/reports/current.json")
    with open(r_path, "w") as f:
        json.dump({"timestamp": time.time(), "pending": len(os.listdir(PENDING))}, f)
        f.flush()
        os.fsync(f.fileno())
    logging.info("Status report generated.")
handlers = {"ping": handle_ping, "backup": handle_backup, "cleanup": handle_cleanup, "status": handle_status}
while True:
    for f in [f for f in os.listdir(PENDING) if f.endswith('.json')]:
        src, dst = os.path.join(PENDING, f), os.path.join(ACTIVE, f)
        try:
            with open(src, 'r') as j: task = json.load(j)
            t_type = task.get("task")
            if t_type in handlers: handlers[t_type](task)
            os.rename(src, dst); os.remove(dst)
        except Exception as e: logging.error(f"Error: {e}")
    time.sleep(2)
