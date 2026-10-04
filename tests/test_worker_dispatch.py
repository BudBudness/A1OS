import pytest

from core.state import system
from core.worker import _execute_payload

@pytest.mark.asyncio
async def test_a1os_worker_dispatches_registered_control_plane_printf():
    action = "printf control-plane"
    assert system.capabilities.has(action)
    result = await _execute_payload("control-plane-regression", {"target": "a1os", "action": action})
    assert result["status"] == "completed"
    assert result["result"]["output"] == "control-plane"
    with pytest.raises(RuntimeError, match="Capability not registered: printf arbitrary"):
        await _execute_payload("arbitrary-command-regression", {"target": "a1os", "action": "printf arbitrary"})
    with pytest.raises(TypeError, match="does not accept execution arguments"):
        await system.execute(action, command="printf arbitrary")

@pytest.mark.asyncio
async def test_a1os_worker_dispatches_observability_capability():
    result = await _execute_payload(
        "observability-regression",
        {"target": "a1os", "action": "observability"},
    )
    assert result["status"] == "completed"
    assert result["result"]["status"] == "observability_snapshot_complete"

@pytest.mark.asyncio
async def test_a1os_consequential_capability_is_not_bypassed():
    with pytest.raises(RuntimeError, match="CONSEQUENCE GATE BLOCKED EXECUTION"):
        await _execute_payload("consequence-gate-regression", {"target": "a1os", "action": "database_repair"})
