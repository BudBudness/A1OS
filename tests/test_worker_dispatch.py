import pytest

from core.state import system
from core.worker import _execute_payload


@pytest.mark.asyncio
async def test_a1os_worker_dispatches_only_registered_control_plane_printf():
    action = "printf control-plane"

    assert system.capabilities.has(action)
    result = await _execute_payload(
        "control-plane-regression",
        {"target": "a1os", "action": action},
    )

    assert result == {
        "task_id": "control-plane-regression",
        "status": "completed",
        "result": {
            "status": "success",
            "output": "control-plane",
            "returncode": 0,
        },
    }

    with pytest.raises(RuntimeError, match="Capability not registered: printf arbitrary"):
        await _execute_payload(
            "arbitrary-command-regression",
            {"target": "a1os", "action": "printf arbitrary"},
        )

    with pytest.raises(TypeError, match="does not accept execution arguments"):
        await system.execute(action, command="printf arbitrary")
