"""A1OS edge provider selection boundary."""

import os

from .edge_provider_runtime import (
    ADAPTERS,
    SUPPORTED_EDGE_PROVIDERS,
)


def selected_provider() -> str:
    provider = os.environ.get(
        "A1OS_EDGE_PROVIDER",
        "cloudflare",
    ).strip().lower()

    if provider not in SUPPORTED_EDGE_PROVIDERS:
        raise ValueError(
            f"Unsupported A1OS_EDGE_PROVIDER={provider}. "
            f"Supported: {sorted(SUPPORTED_EDGE_PROVIDERS)}"
        )

    return provider


def selected_adapter():
    return ADAPTERS[selected_provider()]()


if __name__ == "__main__":
    provider = selected_provider()
    adapter = selected_adapter()

    print(f"EDGE_PROVIDER={provider}")
    print(f"EDGE_EXECUTABLE={'YES' if adapter.executable() else 'NO'}")
