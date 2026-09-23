"""Lightweight deterministic secops factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("secops", "secops", "security-operations-plan", true)

if __name__ == "__main__":
    cli(ENGINE)
