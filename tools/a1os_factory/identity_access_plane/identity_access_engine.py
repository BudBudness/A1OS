"""Deterministic identity-access factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("identity-access", "identity-access", "identity-policy", False)

if __name__ == "__main__":
    cli(ENGINE)
