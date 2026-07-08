import urllib.request, json, sqlite3
class NotificationEngine:
    def __init__(self, db="a1os_state.db"):
        self.db = db
        self.webhook_url = "https://httpbin.org/post"
    async def dispatch_external_alert(self, topic: str, payload: dict):
        req = urllib.request.Request(self.webhook_url, data=json.dumps({"topic": topic, "metrics": payload}, sort_keys=True).encode("utf-8"), headers={"Content-Type": "application/json", "User-Agent": "A1OS-Gateway-Engine"})
        status, err = "SENT", None
        try:
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status != 200: status = f"FAILED_HTTP_{resp.status}"
        except Exception as e:
            status = "FAILED_NETWORK_OUTAGE"
            err = str(e)
        with sqlite3.connect(self.db, timeout=10.0) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO notification_history (topic, payload, status, error_context) VALUES (?,?,?,?)", (topic, json.dumps(payload), status, err))
            conn.commit()
