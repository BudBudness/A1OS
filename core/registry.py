import logging
import os
import requests

class PingProvider:
    def execute(self, action, payload):
        return f"Pong! Received: {payload}"

class FileProvider:
    def execute(self, action, payload):
        if action == "write":
            with open(payload["path"], "w") as f:
                f.write(payload["content"])
            return f"File {payload['path']} written."
        return "Unknown file action."

class NetworkProvider:
    def execute(self, action, payload):
        if action == "get":
            response = requests.get(payload["url"], timeout=5)
            return {"status": response.status_code, "text": response.text[:100]}
        return "Unknown network action."

class Registry:
    def __init__(self):
        self.providers = {
            "system": PingProvider(),
            "file": FileProvider(),
            "network": NetworkProvider()
        }
    async def initialize(self):
        logging.info("Registry initialized with system, file, and network providers.")
    def get_provider(self, domain):
        return self.providers.get(domain)

registry = Registry()
