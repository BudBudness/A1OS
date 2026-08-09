import asyncio

class Cluster:
    def __init__(self, runtime):
        self.runtime = runtime
        self.nodes = []

    def register_node(self, node):
        self.nodes.append(node)

    async def broadcast(self, event):
        # fanout execution across nodes (logical layer)
        tasks = [node.execute(event) for node in self.nodes if hasattr(node, "execute")]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
