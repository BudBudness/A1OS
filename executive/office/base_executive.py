from workflow.engine import WorkflowEngine

class BaseExecutive:
    def __init__(self, name, title):
        self.name = name
        self.title = title
        self.managed_handles = {}

    def add_handle(self, dept_name, handle):
        self.managed_handles[dept_name] = handle

    def delegate_down(self, dept_name, task):
        # 1. Initiate Workflow
        task_id = WorkflowEngine.create_task(self.title, dept_name, task)
        
        # 2. Transition to Executing
        WorkflowEngine.transition(task_id, "EXECUTING")
        
        # 3. Perform work via handle
        handle = self.managed_handles.get(dept_name)
        if handle:
            result = handle.delegate(task)
            
            # 4. Finalize
            WorkflowEngine.transition(task_id, "COMPLETED")
            return f"Task {task_id} | {result}"
            
        WorkflowEngine.transition(task_id, "FAILED")
        return f"Task {task_id} failed: No authority over {dept_name}"
