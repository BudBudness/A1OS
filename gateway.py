#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime

STATE_PATH = 'data/state.json'
QUEUE_PATH = 'data/queue/agent_command.json'

def get_system_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"error": "Malformed JSON inside state.json"}
    return {"error": "state.json context file not found"}

def parse_natural_language(text):
    normalized = text.lower().strip()
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    # Intent 1: Status Inspection
    if re.search(r'(status|health|check|state|how is|report)', normalized):
        return {"action": "display_status"}
    
    # Intent 2: Data Hydration & Cache Synchronization
    if re.search(r'(refresh|update|hydrate|sync)', normalized):
        category = "all"
        for cat in ["finance", "trading", "procurement", "property"]:
            if cat in normalized:
                category = cat
                break
        return {"task": "refresh_cache", "category": category, "timestamp": ts}
    
    # Intent 3: Log Sanitization & Purging
    if re.search(r'(clean|purge|clear|wipe|sanitize)', normalized):
        return {"task": "purge_audit", "force": True, "timestamp": ts}
    
    # Intent 4: Loop Stabilization & Tuning
    if re.search(r'(optimize|tune|fix|stabilize)', normalized):
        return {"task": "system_optimize", "target": "all", "timestamp": ts}
    
    return None

def execute():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Empty command string received."}))
        sys.exit(1)
        
    user_input = " ".join(sys.argv[1:])
    intent = parse_natural_language(user_input)
    
    if not intent:
        print(json.dumps({"error": f"Parsing Failure: Unable to map intent for: '{user_input}'"}))
        sys.exit(1)
        
    if intent.get("action") == "display_status":
        print(json.dumps({"status": "SUCCESS", "type": "local_read", "data": get_system_state()}, indent=2))
    else:
        os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
        with open(QUEUE_PATH, 'w') as f:
            json.dump(intent, f)
        print(json.dumps({"status": "QUEUED", "type": "task_routing", "payload": intent}, indent=2))

if __name__ == "__main__":
    execute()
