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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("action", "data", "expected_status"),
    [
        ("health_check", {}, "healthy"),
        ("diagnostics", {}, "diagnostics_complete"),
        ("capabilities", {}, "capabilities_available"),
        ("database_repair", {}, "database_verified"),
        ("process_management", {"operation": "health"}, "process_health_complete"),
        ("filesystem_management", {"operation": "exists", "path": "."}, "filesystem_check_complete"),
        ("network_management", {"operation": "interfaces"}, "network_inventory_complete"),
        ("security_audit", {"operation": "processes"}, "security_audit_complete"),
        ("service_management", {"operation": "health"}, "service_health_complete"),
    ],
)
async def test_a1os_read_only_capability_surface(action, data, expected_status):
    result = await _execute_payload(
        f"read-only-{action}",
        {"target": "a1os", "action": action, **data},
    )
    assert result["status"] == "completed"
    assert result["result"]["status"] == expected_status


@pytest.mark.asyncio
async def test_a1os_gate_rejects_unsafe_operations_on_read_only_capabilities():
    with pytest.raises(RuntimeError, match="CONSEQUENCE GATE BLOCKED EXECUTION"):
        await _execute_payload(
            "unsafe-process-operation",
            {"target": "a1os", "action": "process_management", "operation": "kill"},
        )
