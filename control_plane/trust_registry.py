from .exceptions import SecurityError
class TrustRegistry:
    def __init__(self): self._trusted = set(); self._path_map = {}
    def is_trusted(self, name): return name in self._trusted
    def allow(self, name): self._trusted.add(name)
    def revoke(self, name): self._trusted.discard(name); self._path_map.pop(name, None)
    def anchor_path(self, name, path):
        if name in self._path_map and self._path_map[name] != path: raise SecurityError("IMMUTABILITY VIOLATION")
        self._path_map[name] = path
