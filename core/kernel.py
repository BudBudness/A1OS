import json, redis, asyncio, logging
from core.registry import registry
from core.executive import executive
from core.persistence import PersistenceManager
from core.security import CapabilityEnforcer
from lib.executor import Executor
from core.goal_generator import GoalGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class A1OSKernel:
    def __init__(self):
        self.executor = Executor()
        self.goal_gen = GoalGenerator()
        self.pm = PersistenceManager()
        self.security = CapabilityEnforcer()
        self.r = None

    async def loop(self):
        # Lazy load Redis to avoid startup lag
        if self.r is None:
            self.r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
            logging.info("Redis connection established.")
            
        while True:
            try:
                task_raw = self.r.rpop("tasks")
                if task_raw:
                    task = json.loads(task_raw)
                    if self.security.validate(task.get("domain"), task.get("action")):
                        await executive.orchestrate(task)
                        provider = registry.get_provider(task.get("domain"))
                        if provider:
                            result = provider.execute(task.get("action"), task.get("payload"))
                            self.pm.save_state(task.get("action"), result)
                            logging.info(f"Finalized: {result}")
            except Exception as e:
                logging.error(f"Kernel Critical: {e}")
            await asyncio.sleep(1)
