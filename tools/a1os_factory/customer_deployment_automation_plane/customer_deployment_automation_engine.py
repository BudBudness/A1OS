"""Deterministic customer-deployment factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("customer-deployment", "customer-deployment", "deployment-plan", true)

if __name__ == "__main__":
    cli(ENGINE)
