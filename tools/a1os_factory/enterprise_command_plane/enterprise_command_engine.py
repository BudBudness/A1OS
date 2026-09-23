"""Deterministic enterprise-command factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("enterprise-command", "enterprise-command", "command-plan", True)

if __name__ == "__main__":
    cli(ENGINE)
