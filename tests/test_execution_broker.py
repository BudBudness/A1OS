import asyncio
import os
from pathlib import Path

import pytest

from core.control_plane import execution_broker
from core.control_plane.execution_broker import ExecutionBroker, ExecutionDenied


def test_execution_requires_human_approval():
    broker = ExecutionBroker()

    with pytest.raises(ExecutionDenied):
        asyncio.run(broker.execute("printf approved", approved=False))

    assert broker.audit[-1]["event"] == "execution_denied"


def test_approved_execution_runs_through_broker(monkeypatch):
    broker = ExecutionBroker()
    expanduser = os.path.expanduser
    repository_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(
        execution_broker.os.path,
        "expanduser",
        lambda path: repository_root if path == "~/A1OS_RESTORED" else expanduser(path),
    )

    result = asyncio.run(
        broker.execute("printf 'A1OS_BROKER_OK'", approved=True)
    )

    assert result["exit_code"] == 0
    assert result["output"] == "A1OS_BROKER_OK"
    assert broker.audit[-1]["event"] == "execution_result"


def test_empty_command_rejected():
    broker = ExecutionBroker()

    with pytest.raises(ValueError):
        asyncio.run(broker.execute("   ", approved=True))
