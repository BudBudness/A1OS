import json
import re
from typing import Any

from ai.gateway.engine import AIEngine


class JARVISAIInterpreter:
    """
    Semantic language interpreter for JARVIS.

    The model interprets language only.
    It NEVER authorizes or executes an operation.
    A1OS remains the authority for consequence classification,
    authorization, provenance, and execution.
    """

    def __init__(self, ai=None):
        self.ai = ai or AIEngine()

    async def interpret(self, command: str, capabilities: list[str]) -> dict[str, Any]:
        prompt = f"""
You are the semantic interpreter for A1OS JARVIS.

Interpret the user's request into exactly one existing A1OS capability.

USER REQUEST:
{command}

AVAILABLE CAPABILITIES:
{json.dumps(capabilities, ensure_ascii=False)}

Return ONLY valid JSON:
{{
  "intent": "string",
  "capability": "string or null",
  "arguments": {{}},
  "confidence": 0.0
}}

Rules:
- capability MUST be one of the AVAILABLE CAPABILITIES or null.
- Never invent a capability.
- Never claim authorization.
- Never execute anything.
- Never classify risk.
- Never return shell commands.
- If no capability clearly matches, use null.

IMPORTANT SEMANTIC MAPPINGS:
- Questions asking what capabilities A1OS has, what A1OS can do,
  or asking for the capability list MUST map to "capabilities".
- Requests to inspect diagnostics or system diagnostics MUST map
  to "diagnostics".
- Requests specifically asking about observability, monitoring,
  telemetry, metrics, logs, or system observation MUST map to
  "observability" when that capability is available.
- Health/status/online/operational checks may map to "health_check".
- Never map capability-list questions to "digital_world_query".
- Never map diagnostics requests to "health_check" when
  "diagnostics" is available.
"""

        result = await self.ai.think(prompt)
        content = result["response"].strip()

        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*", "", content)
            content = re.sub(r"\s*```$", "", content)

        parsed = json.loads(content)

        # Deterministic semantic normalization for typed A1OS capabilities.
        # JARVIS interprets language only; A1OS remains responsible for
        # consequence classification, authorization, provenance, and execution.
        normalized = command.strip()
        lowered_command = normalized.lower()

        build_phrases = (
            "build ",
            "create ",
            "implement ",
            "modify ",
            "update ",
            "change ",
        )

        deployment_phrases = (
            "deploy ",
            "deploy application",
            "deploy the application",
            "deploy the app",
        )

        if lowered_command.startswith(build_phrases):
            if "build_change" in capabilities:
                parsed["intent"] = normalized
                parsed["capability"] = "build_change"
                parsed["arguments"] = {"request": normalized}
                parsed["confidence"] = 1.0

        elif lowered_command.startswith(deployment_phrases):
            if "deploy_application" in capabilities:
                parsed["capability"] = "deploy_application"

                deployment_text = lowered_command

                template_map = {
                    "professional services": "professional-services",
                    "professional-services": "professional-services",
                    "construction": "construction",
                    "agriculture": "agriculture",
                    "car wash": "car-wash",
                    "car-wash": "car-wash",
                    "charity": "charity",
                    "clinic": "clinic",
                    "events": "events",
                    "hotel": "hotel",
                    "logistics": "logistics",
                    "music": "music",
                    "real estate": "real-estate",
                    "real-estate": "real-estate",
                    "restaurant": "restaurant",
                    "retail": "retail",
                    "salon": "salon",
                    "school": "school",
                }

                template_slug = "professional-services"

                for phrase, slug in template_map.items():
                    if phrase in deployment_text:
                        template_slug = slug
                        break

                parsed["arguments"] = {
                    "product": template_slug,
                    "template_slug": template_slug,
                    "environment": "production",
                }
            else:
                parsed["intent"] = "unknown"
                parsed["capability"] = None
                parsed["confidence"] = 0.0
                parsed["arguments"] = {}

        if parsed.get("capability") is not None and parsed.get("capability") not in capabilities:
            parsed["capability"] = None
            parsed["confidence"] = 0.0

        return parsed
