from a1os.memory.vector.store import search

class Router:
    def route(self,task):
        t=str(task).lower()
        if "research" in t: return "research"
        if "plan" in t: return "planner"
        if "critic" in t or "review" in t: return "critic"
        return "executor"

    def context(self,task):
        return search(task,3)
