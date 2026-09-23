"""Deterministic data-intelligence factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("data-intelligence", "data-intelligence", "data-contract", False)

if __name__ == "__main__":
    cli(ENGINE)
