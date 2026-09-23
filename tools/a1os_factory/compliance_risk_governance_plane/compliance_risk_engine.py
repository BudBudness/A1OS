"""Deterministic compliance-risk factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("compliance-risk", "compliance-risk", "risk-policy", False)

if __name__ == "__main__":
    cli(ENGINE)
