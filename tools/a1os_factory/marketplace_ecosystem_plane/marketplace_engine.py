"""Deterministic marketplace factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("marketplace", "marketplace", "marketplace-contract", false)

if __name__ == "__main__":
    cli(ENGINE)
