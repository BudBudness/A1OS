class CEO:
    def __init__(self, name):
        self.name = name
        self.staff = {}

    def hire_executive(self, role, executive):
        self.staff[role] = executive

    def command(self, role, dept, task):
        exec_officer = self.staff.get(role)
        if exec_officer:
            return exec_officer.delegate_down(dept, task)
        return f"Role {role} not found in Executive Office."
