"""Lightweight deterministic workflow-orchestration factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("workflow-orchestration", "workflow-orchestration", "orchestration-plan", true)

if __name__ == "__main__":
    cli(ENGINE)
