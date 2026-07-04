
from typing import Dict, Optional
from company.base import BaseAgent

class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        return self._agents.get(name)

