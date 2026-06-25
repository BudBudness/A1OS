class Agent:
    def __init__(self,name,role):
        self.name=name
        self.role=role

    def run(self,input_data,context):
        return {
            "agent":self.name,
            "role":self.role,
            "input":str(input_data),
            "context_size":len(context),
            "output":f"{self.role}_processed:{input_data}"
        }
