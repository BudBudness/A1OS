import os
import logging

logger = logging.getLogger("A1OS-SecretsManager")

class SecretsManager:
    def __init__(self):
        # In a full production environment, this vault dictionary would be unsealed/decrypted using a master HSM key.
        self._vault = {
            "openai_key": "sk-secure-mock-open-ai-key-12345",
            "discord_token": "bot-token-87654321-secure"
        }

    def inject_secrets_to_env(self, module_name: str, allowed_keys: list):
        """Injects authorized secrets into the isolated process environment space."""
        for key in allowed_keys:
            if key in self._vault:
                env_var_name = f"A1OS_SECRET_{key}"
                os.environ[env_var_name] = self._vault[key]
                logger.info(f"[SECRETS] 🔑 Vault injected secure env var '{env_var_name}' for subprocess: {module_name}")
            else:
                logger.error(f"[SECRETS] ❌ Unauthorized or non-existent secret requested: {key}")
