"""Lightweight deterministic ai-governance factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("ai-governance", "ai-governance", "governance-policy", false)

if __name__ == "__main__":
    cli(ENGINE)
