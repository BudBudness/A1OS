"""Lightweight deterministic disaster-recovery factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("disaster-recovery", "disaster-recovery", "recovery-plan", true)

if __name__ == "__main__":
    cli(ENGINE)
