import asyncio, json, subprocess
class A1OSWorker:
    def __init__(self, node_id): self.node_id = node_id
    async def run(self):
        server = await asyncio.start_server(self.handle_rpc, '0.0.0.0', 8888)
        async with server: await server.serve_forever()
    async def handle_rpc(self, reader, writer):
        data = (await reader.read(1024)).decode()
        method, payload = data.split(':', 1)
        task = json.loads(payload)
        proc = await asyncio.create_subprocess_shell(task['cmd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        writer.write(json.dumps({"status": "done", "out": stdout.decode()}).encode())
        await writer.drain()
        writer.close()
