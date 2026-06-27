import requests, json, time, threading
from datetime import datetime

class AgentCommunication:
    def __init__(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while self.running:
            try:
                agents = requests.get("http://localhost:8086/agents", headers={"X-API-Key": "f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108"}).json()
                for agent in agents:
                    if agent["status"] == "working":
                        # Send a message to other agents
                        msg = f"{agent['name']} is processing tasks"
                        print(f"📨 {msg}")
                time.sleep(45)
            except Exception as e:
                print(f"Comm error: {e}")
                time.sleep(10)
