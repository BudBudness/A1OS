import asyncio
import json
import redis.asyncio as redis
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.redis = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    async def run(self):
        while True:
            now = datetime.now().strftime("%H:%M")
            tasks = await self.redis.smembers("scheduled_tasks")
            for task_json in tasks:
                task = json.loads(task_json)
                if task["time"] == now:
                    await self.redis.rpush("tasks", json.dumps(task["payload"]))
            await asyncio.sleep(60)
