import os
from pathlib import Path
import httpx

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

if _ENV_FILE.is_file():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _key, _value = _line.split("=", 1)
        _key = _key.strip()
        _value = _value.strip()
        if _key and _key not in os.environ:
            os.environ[_key] = _value


class AIEngine:
    def __init__(self):
        self.gateway_url = os.getenv(
            "CLOUDFLARE_AI_GATEWAY_URL",
            "https://pyongcity.org/compat/chat/completions",
        )
        self.token = os.getenv("CLOUDFLARE_AI_GATEWAY_TOKEN")
        self.model = os.getenv(
            "CLOUDFLARE_AI_GATEWAY_MODEL",
            "workers-ai/@cf/meta/llama-3.1-8b-instruct-fast",
        )
        self.timeout = float(os.getenv("CLOUDFLARE_AI_GATEWAY_TIMEOUT", "30"))

    async def think(self, prompt):
        if not self.token:
            raise RuntimeError("CLOUDFLARE_AI_GATEWAY_TOKEN is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.gateway_url,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )

        if content is None:
            raise RuntimeError("Cloudflare AI Gateway returned no assistant content")

        return {
            "response": content,
            "model": data.get("model", self.model),
            "id": data.get("id"),
            "usage": data.get("usage", {}),
        }
