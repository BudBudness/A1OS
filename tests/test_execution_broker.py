import asyncio

import pytest

from core.control_plane.execution_broker import ExecutionBroker, ExecutionDenied


def test_execution_requires_human_approval():
    broker = ExecutionBroker()

    with pytest.raises(ExecutionDenied):
        asyncio.run(broker.execute("printf approved", approved=False))

    assert broker.audit[-1]["event"] == "execution_denied"


def test_approved_execution_requires_capability_bound_authorization():
    broker = ExecutionBroker()

    with pytest.raises(Exception, match="Capability-bound authorization is required"):
        asyncio.run(
            broker.execute("printf 'A1OS_BROKER_OK'", approved=True)
        )


def test_empty_command_rejected():
    broker = ExecutionBroker()

    with pytest.raises(ValueError):
        asyncio.run(broker.execute("   ", approved=True))
