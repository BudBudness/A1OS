import os, time, json, logging
PENDING, ACTIVE, LOG = "data/tasks/pending", "data/tasks/active", "logs/ops/daemon.log"
logging.basicConfig(filename=LOG, level=logging.INFO, format='%(asctime)s - %(message)s')
while True:
    for f in [f for f in os.listdir(PENDING) if f.endswith('.json')]:
        try:
            with open(os.path.join(PENDING, f), 'r') as j: task = json.load(j)
            logging.info(f"Executing: {task}")
            os.rename(os.path.join(PENDING, f), os.path.join(ACTIVE, f))
            os.remove(os.path.join(ACTIVE, f))
        except Exception as e: logging.error(f"Error: {e}")
    time.sleep(2)
