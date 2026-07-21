import json, uuid, os, sys
from datetime import datetime

def inject(dept, t_type, payload):
    task = {
        "id": str(uuid.uuid4()),
        "department": dept,
        "task_type": t_type,
        "payload": payload,
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "approval_state": "APPROVED"
    }
    path = f"{os.environ['HOME']}/A1OS/data/tasks/pending/{task['id']}.json"
    with open(path, 'w') as f:
        json.dump(task, f)
    print(f"Task Injected: {task['id']} [{t_type}]")

if __name__ == "__main__":
    inject("SYSTEM", "REFRESH_CACHE", {"category": "test_category"})
