"""Deterministic registry factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("registry", "registry", "registry-record", false)

if __name__ == "__main__":
    cli(ENGINE)
