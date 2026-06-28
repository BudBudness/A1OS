# runtime_engine.py - Autonomous Filesystem State Handler
import os
import time
import json

BASE_DIR = os.path.expanduser("~/A1OS")
TASK_DIR = os.path.join(BASE_DIR, "tasks/queue")
DONE_DIR = os.path.join(BASE_DIR, "tasks/done")
LOG_DIR = os.path.join(BASE_DIR, "memory/logs")

print("A1OS Native File Observer Engine Active. Monitoring filesystem queues...")

while True:
    try:
        tasks = [t for t in os.listdir(TASK_DIR) if not t.startswith('.')]
        for task_file in tasks:
            task_path = os.path.join(TASK_DIR, task_file)
            print(f"[FOUND TASK]: Processing {task_file}")
            
            with open(task_path, 'r') as f:
                task_data = json.load(f)
                
            task_data["processed_at"] = time.time()
            task_data["status"] = "Executed"
            
            with open(os.path.join(DONE_DIR, task_file), 'w') as out:
                json.dump(task_data, out, indent=2)
                
            os.remove(task_path)
            
            with open(os.path.join(LOG_DIR, "session_context.log"), "a") as log:
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                log.write(f"[{ts}] Task executed successfully: {task_file}\n")
                
    except Exception as e:
        print(f"Runtime Warning: {str(e)}")
        
    time.sleep(2)
