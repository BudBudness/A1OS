from .exceptions import CapabilityViolation
class CapabilityManager:
    def __init__(self): self._caps = {}
    def register(self, name, apis): self._caps[name] = set(apis)
    def get_manifest(self, name): return list(self._caps.get(name, set()))
    def anchor(self, name, caps): self._caps[name] = set(caps)
    def enforce(self, name, api):
        if api not in self._caps.get(name, set()): raise CapabilityViolation(f"{name} lacks {api}")
