from executive.office.base_executive import BaseExecutive

class CFO(BaseExecutive):
    def __init__(self, name): super().__init__(name, "CFO")

class CTO(BaseExecutive):
    def __init__(self, name): super().__init__(name, "CTO")

class COO(BaseExecutive):
    def __init__(self, name): super().__init__(name, "COO")
