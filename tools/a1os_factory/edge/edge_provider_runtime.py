"""A1OS provider-neutral edge execution contract."""

from dataclasses import dataclass
from typing import Literal

EdgeProvider = Literal[
    "cloudflare",
    "tailscale",
    "nginx",
    "caddy",
    "direct",
]

SUPPORTED_EDGE_PROVIDERS = {
    "cloudflare",
    "tailscale",
    "nginx",
    "caddy",
    "direct",
}


@dataclass(frozen=True)
class EdgeExecutionRequest:
    provider: EdgeProvider
    hostname: str
    origin: str


class EdgeProviderAdapter:
    provider: EdgeProvider

    def validate(self, request: EdgeExecutionRequest) -> None:
        if request.provider not in SUPPORTED_EDGE_PROVIDERS:
            raise ValueError(
                f"Unsupported edge provider: {request.provider}"
            )

        if not request.hostname:
            raise ValueError("hostname is required")

        if not request.origin:
            raise ValueError("origin is required")

    def executable(self) -> bool:
        return False

    def plan(self, request: EdgeExecutionRequest) -> dict:
        self.validate(request)
        return {
            "provider": request.provider,
            "hostname": request.hostname,
            "origin": request.origin,
            "executable": self.executable(),
            "execution": "plan-only",
        }


class CloudflareAdapter(EdgeProviderAdapter):
    provider = "cloudflare"

    def executable(self) -> bool:
        return True


class TailscaleAdapter(EdgeProviderAdapter):
    provider = "tailscale"


class NginxAdapter(EdgeProviderAdapter):
    provider = "nginx"


class CaddyAdapter(EdgeProviderAdapter):
    provider = "caddy"


class DirectAdapter(EdgeProviderAdapter):
    provider = "direct"

    def executable(self) -> bool:
        return True

    def plan(self, request: EdgeExecutionRequest) -> dict:
        self.validate(request)
        return {
            "provider": request.provider,
            "hostname": request.hostname,
            "origin": request.origin,
            "executable": True,
            "execution": "direct",
            "requirements": [
                "origin_listener",
                "reachable_host",
                "optional_dns_record",
                "optional_tls_termination",
            ],
        }


ADAPTERS = {
    "cloudflare": CloudflareAdapter,
    "tailscale": TailscaleAdapter,
    "nginx": NginxAdapter,
    "caddy": CaddyAdapter,
    "direct": DirectAdapter,
}
