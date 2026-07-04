class BaseModule:
    def __init__(self):
        self.name = self.__class__.__name__

    def get_status(self):
        return f"{self.name} is operational."

    def execute(self, action, **kwargs):
        raise NotImplementedError("Each module must implement an execute method.")
