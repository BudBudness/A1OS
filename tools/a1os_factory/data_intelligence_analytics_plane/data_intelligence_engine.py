"""Deterministic data-analytics factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("data-analytics", "data-analytics", "analytics-contract", False)

if __name__ == "__main__":
    cli(ENGINE)
