import os
import json
import logging

logger = logging.getLogger("A1OS-SDK")

class A1OSPlugin:
    def __init__(self, name: str):
        self.name = name
        self.events_map = {}

    def register_event(self, topic: str):
        def decorator(func):
            self.events_map[topic] = func
            return func
        return decorator

    def get_secret(self, key: str) -> str:
        """Fetch runtime injected secrets securely from the isolated subprocess environment."""
        secret_val = os.getenv(f"A1OS_SECRET_{key}")
        if not secret_val:
            logger.warning(f"[{self.name}] ⚠️ Requested secret '{key}' not found in environment isolation scope.")
        return secret_val or ""

    def execute_event(self, topic: str, payload: dict):
        if topic in self.events_map:
            return self.events_map[topic](payload)
        logger.warning(f"[{self.name}] 🔸 Unhandled event topic intercepted: {topic}")
