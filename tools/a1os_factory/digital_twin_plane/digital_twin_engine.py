"""Lightweight deterministic digital-twin factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("digital-twin", "digital-twin", "twin-model", false)

if __name__ == "__main__":
    cli(ENGINE)
