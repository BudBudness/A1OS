import time, json, urllib.request, sqlite3
from security.auth.engine import AuthEngine

TARGET_URL = "http://localhost:3001/v1/execute"
auth = AuthEngine()
DB_PATH = "a1os_state.db"

def run_recovery_worker():
    # Dynamic Auto-Flush Optimization Loop for cached outage logs
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT id, topic, payload FROM notification_history WHERE status='FAILED_NETWORK_OUTAGE' LIMIT 5")
            records = c.fetchall()
            if records:
                print(f"   🔄 [Cron Daemon Worker] Recovered {len(records)} deferred outage vectors. Flushing to gateway transport...")
                for row in records:
                    rid, topic, payload_str = row
                    p_data = json.loads(payload_str)
                    # Forward as structural background task executions
                    req_payload = {"target": "telemetry_cron", "role": "cron_scheduler", "action": "process_cron_metrics", "data": p_data}
                    sig = auth.generate_signature(req_payload)
                    req = urllib.request.Request(TARGET_URL, data=json.dumps(req_payload, sort_keys=True).encode("utf-8"), headers={"Content-Type": "application/json", "X-Signature": sig}, method="POST")
                    try:
                        with urllib.request.urlopen(req, timeout=2) as resp:
                            if resp.status == 200:
                                c.execute("UPDATE notification_history SET status='FLUSHED_RECOVERED' WHERE id=?", (rid,))
                    except Exception: pass
                conn.commit()
    except Exception: pass

def run_loop():
    print("A1OS CRON MATRIX AUTOMATION HEARTBEAT active.")
    for cycle in range(2):
        run_recovery_worker()
        # Dispatch system memory telemetry
        metrics = {"timestamp": time.time(), "battery_level": 100, "memory_free_mb": 2048}
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemFree" in line:
                        metrics["memory_free_mb"] = int(line.split()[1]) // 1024
                        break
        except Exception: pass
        
        payload = {"target": "telemetry_cron", "role": "cron_scheduler", "action": "process_cron_metrics", "data": metrics}
        try:
            sig = auth.generate_signature(payload)
            req = urllib.request.Request(TARGET_URL, data=json.dumps(payload, sort_keys=True).encode("utf-8"), headers={"Content-Type": "application/json", "X-Signature": sig}, method="POST")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200: print(f"   [Cron Pulse] Telemetry envelope committed securely.")
        except Exception as e: print(f"   [Cron Pulse Dropped] {e}")
        time.sleep(1)

if __name__ == "__main__": run_loop()
