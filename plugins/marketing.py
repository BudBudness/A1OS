from organization.departments.base_department import BaseDepartment

class MarketingDepartment(BaseDepartment):
    def __init__(self):
        super().__init__("Marketing", "Growth_Bot")
        self.kpis = {"budget": 200000, "spent": 0}
        
    def run_campaign(self, campaign_name):
        return f"Marketing launched {campaign_name}."
