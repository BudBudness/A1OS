"""Deterministic customer-success factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("customer-success", "customer-success", "success-workflow", False)

if __name__ == "__main__":
    cli(ENGINE)
