"""Model gateway boundary.

The gateway is intentionally non-authoritative: model output is returned as
interpretation only and cannot authorize execution.
"""

from typing import Any, Dict


class AIEngine:
    """Provider-neutral interpretation boundary."""

    async def think(
        self, prompt: str, *, provider: str = "unconfigured"
    ) -> Dict[str, Any]:
        if not isinstance(prompt, str) or not prompt.strip():
            return {
                "status": "rejected",
                "reason": "prompt_required",
                "execution_authorized": False,
            }

        if provider == "unconfigured":
            return {
                "status": "unavailable",
                "reason": "model_provider_not_configured",
                "prompt": prompt,
                "execution_authorized": False,
            }

        return {
            "status": "not_implemented",
            "reason": "provider_adapter_required",
            "provider": provider,
            "prompt": prompt,
            "execution_authorized": False,
        }
