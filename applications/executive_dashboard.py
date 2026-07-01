from applications.base_app import BaseApplication

class ExecutiveDashboard(BaseApplication):
    def __init__(self):
        super().__init__(
            name="Executive Dashboard",
            description="Central command for monitoring departmental health and audit logs.",
            required_plugins=["logger", "audit_monitor"]
        )

    def run(self, departments):
        self.status = "running"
        print(f"--- {self.name} ---")
        for dept in departments:
            # Aggregate status from the department framework
            report = dept.generate_report()
            print(f"Department: {report['department']} | Status: {report['status']}")
        return "Dashboard Rendered"

# Test Orchestration
if __name__ == "__main__":
    from organization.departments.base_department import BaseDepartment
    
    # Mock departments
    eng = BaseDepartment("Engineering", "Eddie Billions")
    fin = BaseDepartment("Finance", "Eddie Billions")
    
    dashboard = ExecutiveDashboard()
    if dashboard.validate_environment():
        dashboard.run([eng, fin])
