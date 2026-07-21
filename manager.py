import asyncio
from core.execution.v2.registry.node_registry import NodeRegistry
class A1OSManager:
    def __init__(self): self.registry = NodeRegistry()
    async def heartbeat_loop(self):
        while True:
            active = self.registry.get_active_nodes()
            print(f"[+] Active Nodes: {active}")
            await asyncio.sleep(5)
