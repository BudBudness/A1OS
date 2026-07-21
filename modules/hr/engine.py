from typing import Dict, List
import uuid

class HREngine:
    def __init__(self):
        self.employees: Dict[str, Dict] = {}
        self.departments: Dict[str, Dict] = {}
        self.timecards: List[Dict] = []
    
    def create_employee(self, data: Dict) -> str:
        employee_id = str(uuid.uuid4())
        self.employees[employee_id] = {
            "id": employee_id,
            **data
        }
        return employee_id
    
    def create_department(self, name: str, manager: str) -> str:
        dept_id = str(uuid.uuid4())
        self.departments[dept_id] = {
            "id": dept_id,
            "name": name,
            "manager": manager
        }
        return dept_id
    
    def clock_in(self, employee_id: str):
        self.timecards.append({
            "employee_id": employee_id,
            "type": "in",
            "timestamp": "now"
        })
    
    def get_employee(self, employee_id: str) -> Dict:
        return self.employees.get(employee_id, {})
