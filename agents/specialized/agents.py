class BaseAgent:
    def __init__(self,name):
        self.name=name

    def act(self,task,ctx):
        return {
            "agent":self.name,
            "task":task,
            "context":ctx,
            "output":f"{self.name}_executed:{task}"
        }

AGENTS={
    "research":BaseAgent("research"),
    "planner":BaseAgent("planner"),
    "executor":BaseAgent("executor"),
    "critic":BaseAgent("critic")
}
