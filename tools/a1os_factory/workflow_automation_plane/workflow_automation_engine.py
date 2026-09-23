"""Deterministic workflow-automation factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("workflow-automation", "workflow-automation", "workflow-definition", False)

if __name__ == "__main__":
    cli(ENGINE)
