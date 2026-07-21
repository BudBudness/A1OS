
from company.base import BaseAgent
import uuid

class LifecycleManager:
    @staticmethod
    def spawn(agent_class: type, *args, **kwargs) -> BaseAgent:
        agent = agent_class(*args, **kwargs)
        # Initialization hooks (logging, monitoring)
        return agent

