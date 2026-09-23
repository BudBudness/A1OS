"""Lightweight deterministic knowledge-graph factory engine."""
from tools.a1os_factory.engine_runtime import cli, make_engine

ENGINE = make_engine("knowledge-graph", "knowledge-graph", "graph-model", false)

if __name__ == "__main__":
    cli(ENGINE)
