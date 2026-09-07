import os, json
BASE = "/data/data/com.termux/files/home/A1OS"
print(f"--- SYSTEM HEALTH: {os.popen('date').read().strip()} ---")
print(f"Pending: {len(os.listdir(f'{BASE}/data/tasks/pending/'))}")
print(f"Archived: {len(os.listdir(f'{BASE}/data/tasks/archive/'))}")
print(f"DLQ (Failures): {len(os.listdir(f'{BASE}/data/tasks/dlq/'))}")
