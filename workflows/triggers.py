import time, threading, requests, json
from datetime import datetime

class WorkflowTriggers:
    def __init__(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while self.running:
            try:
                workflows = requests.get("http://localhost:8086/workflows", headers={"X-API-Key": "f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108"}).json()
                for wf in workflows:
                    if wf["status"] == "pending":
                        requests.post(f"http://localhost:8086/workflows/{wf['id']}/execute", headers={"X-API-Key": "f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108"})
                        print(f"⚡ Triggered workflow: {wf['name']}")
                time.sleep(60)
            except Exception as e:
                print(f"Trigger error: {e}")
                time.sleep(10)
