import asyncio
import json
import logging
import redis.asyncio as redis
from core.registry import registry
from core.pm import PersistenceManager

class A1OSKernel:
    def __init__(self):
        self.redis = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
        self.pm = PersistenceManager()
    
    async def loop(self):
        logging.info("A1OS Kernel started.")
        while True:
            # blpop returns (queue_name, task_json)
            task_data = await self.redis.blpop("tasks")
            if task_data:
                _, task_json = task_data
                task = json.loads(task_json)
                
                domain = task.get("domain")
                action = task.get("action")
                payload = task.get("payload")
                
                provider = registry.get_provider(domain)
                if provider:
                    result = provider.execute(action, payload)
                    self.pm.save_state(action, result)
                    logging.info(f"Finalized: {result}")
