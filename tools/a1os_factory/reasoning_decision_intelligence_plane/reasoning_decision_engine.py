"""Deterministic reasoning-decision factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("reasoning-decision", "reasoning-decision", "decision-record", false)

if __name__ == "__main__":
    cli(ENGINE)
