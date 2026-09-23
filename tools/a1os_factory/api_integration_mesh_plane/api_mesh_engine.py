"""Deterministic api-integration factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("api-integration", "api-integration", "api-contract", false)

if __name__ == "__main__":
    cli(ENGINE)
