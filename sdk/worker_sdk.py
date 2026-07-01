from system.persistence import AuditLogger

class WorkerSDK:
    def __init__(self, name, role, department):
        self.name = name
        self.role = role
        self.department = department
        self.status = "idle"
        self.logger = AuditLogger()

    def perform_task(self, task_name, action):
        self.status = "working"
        try:
            result = action()
            self.logger.log(self.name, task_name, result, "success")
            return result
        except Exception as e:
            self.logger.log(self.name, task_name, str(e), "failed")
            raise e
        finally:
            self.status = "idle"

    def get_status(self):
        return {"name": self.name, "role": self.role, "status": self.status}
