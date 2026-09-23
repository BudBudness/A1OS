"""Lightweight deterministic workflow-automation factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("workflow-automation", "workflow-automation", "workflow-definition", false)

if __name__ == "__main__":
    cli(ENGINE)
