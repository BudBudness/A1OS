import asyncio
class SecureTransport:
    async def call(self, host, method, data):
        reader, writer = await asyncio.open_connection(host, 8888)
        try:
            writer.write(f"{method}:{json.dumps(data)}".encode())
            await writer.drain()
            return (await reader.read(1024)).decode()
        finally:
            writer.close(); await writer.wait_closed()
