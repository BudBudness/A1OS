import sys
import os

# Ensure SDK is reachable from plugins/ directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from control_plane.sdk import Plugin, Event

class FinancePlugin(Plugin):
    name = "finance_service"
    capabilities = ["database_read", "database_write", "market_data"]

    def on_start(self):
        super().on_start()
        # Securely read vault-injected API keys via SDK
        openai_key = self.get_secret("openai_key")
        if openai_key:
            logger = self._event_handlers.get("logger")
            print(f"[INIT] Vault key verified by {self.name}. Key length: {len(openai_key)}")

    def handle_transaction(self, payload: dict):
        print(f"📈 [BUSINESS LOGIC] Analyzing high-value transaction: {payload.get('tx_id')}")

    def on_stop(self):
        super().on_stop()
