import asyncio, json
class A1OSWorker:
    def __init__(self, node_id): self.node_id = node_id
    async def run(self):
        server = await asyncio.start_server(self.handle_rpc, '0.0.0.0', 8888)
        async with server: await server.serve_forever()
    async def handle_rpc(self, reader, writer):
        data = (await reader.read(1024)).decode()
        method, payload = data.split(':', 1)
        task = json.loads(payload)
        from core.lifecycle import ExecutionBroker, ExecutionRequest

        async def executor(request):
            proc = await asyncio.create_subprocess_shell(
                request.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            return {
                "returncode": proc.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
            }

        result = await ExecutionBroker(executor=executor).execute_async(
            ExecutionRequest(
                command=str(task["cmd"]),
                approval_token=task.get("approval_token"),
                request_id=task.get("request_id"),
            )
        )
        if result.state.value != "completed":
            raise RuntimeError(result.error or "worker_execution_failed")
        return result.result
        stdout, stderr = await proc.communicate()
        writer.write(json.dumps({"status": "done", "out": stdout.decode()}).encode())
        await writer.drain()
        writer.close()
