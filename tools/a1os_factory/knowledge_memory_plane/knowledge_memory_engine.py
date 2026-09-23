"""Deterministic knowledge-memory factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("knowledge-memory", "knowledge-memory", "memory-contract", False)

if __name__ == "__main__":
    cli(ENGINE)
