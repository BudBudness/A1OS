import json, os
STATE_FILE, LOG_FILE, PIPE = os.path.expanduser("~/A1OS/data/state.json"), os.path.expanduser("~/A1OS/data/ingest/logs/audit.jsonl"), os.path.expanduser("~/A1OS/data/queue/task_pipe")
def actuate(action, category):
    with open(PIPE, "w") as f: f.write(f"$HOME/A1OS/ops/actions/{action}.sh {category}\n")
def analyze_and_act():
    if not os.path.exists(LOG_FILE): return
    with open(LOG_FILE, 'r') as f: logs = [json.loads(l) for l in f if l.strip()]
    event = logs[-1] if logs else {}
    status, cat = event.get("status"), event.get("category")
    if not status or status == "active": return
    state = json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}
    attempts = state.get(cat, {}).get("attempts", 0)
    if status == "no_data":
        if attempts < 3:
            actuate("RESTART_SERVICE", cat)
            state[cat] = {"attempts": attempts + 1, "last_action": "RESTART"}
        else: actuate("ALERT_HUMAN", cat)
    elif status == "stale":
        actuate("REFRESH_CACHE", cat)
        state[cat] = {"attempts": 0, "last_action": "REFRESH"}
    with open(STATE_FILE, 'w') as f: json.dump(state, f)
if __name__ == "__main__": analyze_and_act()
