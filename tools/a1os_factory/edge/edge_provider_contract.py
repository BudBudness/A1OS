from dataclasses import dataclass
from typing import Literal


EdgeProvider = Literal[
    "cloudflare",
    "tailscale",
    "nginx",
    "caddy",
    "direct",
]


@dataclass(frozen=True)
class EdgeRoute:
    hostname: str
    service: str
    port: int


@dataclass(frozen=True)
class EdgeProviderConfig:
    provider: EdgeProvider
    routes: tuple[EdgeRoute, ...]
    enabled: bool = True


SUPPORTED_EDGE_PROVIDERS = {
    "cloudflare",
    "tailscale",
    "nginx",
    "caddy",
    "direct",
}


def validate_provider(provider: str) -> str:
    value = provider.strip().lower()

    if value not in SUPPORTED_EDGE_PROVIDERS:
        raise ValueError(
            f"Unsupported edge provider: {value}. "
            f"Supported: {sorted(SUPPORTED_EDGE_PROVIDERS)}"
        )

    return value


def validate_config(config: EdgeProviderConfig) -> None:
    validate_provider(config.provider)

    for route in config.routes:
        if not route.hostname:
            raise ValueError("Edge route hostname cannot be empty")

        if not route.service:
            raise ValueError("Edge route service cannot be empty")

        if not 1 <= route.port <= 65535:
            raise ValueError(f"Invalid edge route port: {route.port}")
