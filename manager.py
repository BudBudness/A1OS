import os, time, json, logging, subprocess
PENDING, ACTIVE, FAILED, LOG = "data/tasks/pending", "data/tasks/active", "data/tasks/failed", "logs/ops/daemon.log"
logging.basicConfig(filename=LOG, level=logging.INFO, format='%(asctime)s - %(message)s')
while True:
    for f in [f for f in os.listdir(PENDING) if f.endswith('.json')]:
        src, dest = os.path.join(PENDING, f), os.path.join(ACTIVE, f)
        try:
            with open(src, 'r') as j: task = json.load(j)
            os.rename(src, dest)
            logging.info(f"Executing: {task}")
            # Dynamic Execution
            if "cmd" in task: subprocess.run(task["cmd"], shell=True, check=True)
            os.remove(dest)
            logging.info(f"Completed: {f}")
        except Exception as e:
            logging.error(f"Error: {e}")
            if os.path.exists(dest): os.rename(dest, os.path.join(FAILED, f))
    time.sleep(2)
