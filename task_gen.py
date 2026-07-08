import os, json, time, random, uuid
PENDING = "/data/data/com.termux/files/home/A1OS/data/tasks/pending"
while True:
    task_id = str(uuid.uuid4())[:8]
    data = {"task": "ping", "id": task_id, "timestamp": time.time()}
    with open(os.path.join(PENDING, f"{task_id}.json"), "w") as f:
        json.dump(data, f)
    time.sleep(random.uniform(1, 5))
