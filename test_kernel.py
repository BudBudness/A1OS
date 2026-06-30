from control_plane.control_plane import ControlPlane
from control_plane.runtime_adapter import RuntimeAdapter

# Mock objects to satisfy the ControlPlane constructor
class MockTrust:
    def is_trusted(self, name): return True
    def allow(self, name): pass
    def bind_path(self, name, path): pass
    def get_path(self, name): return "/path/to/plugin"
class MockSigner:
    def verify(self, name, path): return True
class MockCaps:
    def register(self, name, apis): self.allowed = apis
    def is_allowed(self, name, api): return True
    def get_allowed(self, name): return ["test_api"]
class MockAudit: pass

# Setup
cp = ControlPlane(MockTrust(), MockSigner(), MockCaps(), MockAudit())
adapter = RuntimeAdapter(cp)
cp.set_runtime_adapter(adapter)

# Simulate registration and execution
cp.register_trusted_plugin("test_plugin", "/path/to/plugin", {"sig": "valid"})
result = cp.execute("test_plugin", "test_api", {"data": "payload"})

print(f"Execution Result: {result}")
print(f"Audit Log: {cp.get_security_report()}")
