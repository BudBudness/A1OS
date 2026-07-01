from workflow.engine import WorkflowEngine

class RBAC:
    @staticmethod
    def authorize(user_id, task_id, action):
        task = WorkflowEngine.get_task(task_id)
        return task.owner == user_id
