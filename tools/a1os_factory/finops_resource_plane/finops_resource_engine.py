"""Deterministic finops-resource factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("finops-resource", "finops-resource", "resource-plan", false)

if __name__ == "__main__":
    cli(ENGINE)
