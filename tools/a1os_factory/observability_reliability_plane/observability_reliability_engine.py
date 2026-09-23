"""Deterministic observability-reliability factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("observability-reliability", "observability-reliability", "observability-contract", false)

if __name__ == "__main__":
    cli(ENGINE)
