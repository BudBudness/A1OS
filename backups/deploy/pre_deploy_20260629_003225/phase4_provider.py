
import requests, json
class Provider:
    def __init__(self, endpoint="http://localhost:11434"):
        self.endpoint = endpoint
    def generate(self, prompt):
        resp = requests.post(f"{self.endpoint}/api/generate", json={"prompt": prompt})
        return resp.json()
print("✅ Provider initialized")
