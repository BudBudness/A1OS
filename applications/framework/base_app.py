class BaseApp:
    def __init__(self, name):
        self.name = name
        self.exec_map = {} # Maps dept_name -> executive

    def register_authority(self, dept_name, executive):
        self.exec_map[dept_name] = executive

    def execute(self, dept_name, task):
        executive = self.exec_map.get(dept_name)
        if executive:
            return executive.delegate_down(dept_name, task)
        return f"Error: No executive authorized for {dept_name}"
