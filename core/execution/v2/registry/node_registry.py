import time, json, os
class NodeRegistry:
    STATE_FILE = "/tmp/a1os_nodes.json"
    def _load(self):
        try:
            with open(self.STATE_FILE, "r") as f: return json.load(f)
        except: return {}
    def heartbeat(self, node_id):
        nodes = self._load()
        nodes[node_id] = time.time()
        with open(self.STATE_FILE, "w") as f: json.dump(nodes, f)
    def get_active_nodes(self, timeout=30):
        now = time.time()
        return [nid for nid, last in self._load().items() if now - last < timeout]
