"""Deterministic digital-operations factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("digital-operations", "digital-operations", "operations-workflow", false)

if __name__ == "__main__":
    cli(ENGINE)
