import logging
import os
from typing import Callable, Dict, Any, List

logger = logging.getLogger("A1OS-SDK")

class Event:
    def __init__(self, topic: str, payload: Dict[str, Any], source: str):
        self.topic = topic
        self.payload = payload
        self.metadata = {"source": source}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.topic,
            "payload": self.payload,
            "metadata": self.metadata
        }

class Plugin:
    name: str = "base_plugin"
    capabilities: List[str] = []

    def __init__(self):
        self._event_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}

    def register_handler(self, topic: str, handler: Callable[[Dict[str, Any]], None]):
        self._event_handlers[topic] = handler
        logger.info(f"[{self.name}] ⚓ Handler registered for event topic: '{topic}'")

    def get_secret(self, key: str) -> str:
        """Fetch environment-injected API keys securely without touching files."""
        env_var = f"A1OS_SECRET_{key}"
        val = os.getenv(env_var, "")
        if not val:
            logger.warning(f"[{self.name}] ⚠️ Secret {key} not found in restricted environment.")
        return val

    def on_start(self):
        """Lifecycle hook triggered when the kernel initializes the plugin."""
        logger.info(f"[{self.name}] 🟢 Lifecycle hook: on_start() executed.")

    def on_event(self, event: Event):
        """Dispatches incoming event payloads to registered handlers automatically."""
        handler = self._event_handlers.get(event.topic)
        if handler:
            logger.info(f"[{self.name}] ⚡ Processing event payload for topic: '{event.topic}'")
            try:
                handler(event.payload)
            except Exception as e:
                logger.error(f"[{self.name}] 💥 Handler error on topic '{event.topic}': {e}")
        else:
            logger.warning(f"[{self.name}] 🔸 Unhandled or unregistered event topic: '{event.topic}'")

    def on_stop(self):
        """Lifecycle hook triggered when the control plane revokes plugin execution."""
        logger.info(f"[{self.name}] 🔴 Lifecycle hook: on_stop() executed.")
