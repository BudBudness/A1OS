import os, json
BASE = "/data/data/com.termux/files/home/A1OS"
from datetime import datetime
print(f"--- SYSTEM HEALTH: {datetime.now().astimezone().isoformat()} ---")
print(f"Pending: {len(os.listdir(f'{BASE}/data/tasks/pending/'))}")
print(f"Archived: {len(os.listdir(f'{BASE}/data/tasks/archive/'))}")
print(f"DLQ (Failures): {len(os.listdir(f'{BASE}/data/tasks/dlq/'))}")
