from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.registry import Registry


def test_registry_loads_initial_capabilities_and_workflows():
    registry = Registry(ROOT / "registry")
    registry.discover()
    assert len(registry.capabilities) == 10
    assert len(registry.workflows) == 10
    assert "database.postgresql" in registry.capabilities
    assert "messaging.kafka" in registry.capabilities
    assert "database.postgresql.provision" in registry.workflows
    assert "infrastructure.kubernetes.provision" in registry.workflows


def test_workflow_capabilities_resolve():
    registry = Registry(ROOT / "registry")
    registry.discover()
    for workflow_id, workflow in registry.workflows.items():
        capability = workflow["spec"]["capability"]["id"]
        assert capability in registry.capabilities, workflow_id


if __name__ == "__main__":
    test_registry_loads_initial_capabilities_and_workflows()
    test_workflow_capabilities_resolve()
    print("A1OS engineering registry verification: PASS")
