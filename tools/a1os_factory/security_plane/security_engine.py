"""Deterministic security factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("security", "security", "security-policy", False)

if __name__ == "__main__":
    cli(ENGINE)
