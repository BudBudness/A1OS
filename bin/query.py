import json
import sys
import os

def query_logs(action=None):
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "state.log")
    if not os.path.exists(log_path):
        print("Log file not found.")
        return
    with open(log_path, "r") as f:
        for line in f:
            entry = json.loads(line)
            if not action or entry["action"] == action:
                print(f"[{entry['timestamp']}] {entry['action']}: {entry['result']}")

if __name__ == "__main__":
    query_logs(sys.argv[1] if len(sys.argv) > 1 else None)
