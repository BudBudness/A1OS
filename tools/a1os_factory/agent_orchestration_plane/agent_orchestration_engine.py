"""Deterministic workflow-orchestration factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("workflow-orchestration", "workflow-orchestration", "orchestration-plan", True)

if __name__ == "__main__":
    cli(ENGINE)
