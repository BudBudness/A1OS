"""Deterministic self-improvement factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("self-improvement", "self-improvement", "improvement-plan", True)

if __name__ == "__main__":
    cli(ENGINE)
