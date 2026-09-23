"""Deterministic infrastructure factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("infrastructure", "infrastructure", "infrastructure-plan", False)

if __name__ == "__main__":
    cli(ENGINE)
