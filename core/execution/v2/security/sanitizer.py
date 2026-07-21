class InputSanitizer:
    def __init__(self):
        self.schemas = {"process_data": ["task_id", "action", "data"]}

    def validate(self, action, data):
        if action in self.schemas:
            for key in self.schemas[action]:
                if key not in data and key != "data":
                    raise ValueError(f"Missing required field: {key}")
        return True
