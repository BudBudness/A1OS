from modules.finance import Finance
from modules.executive_dashboard import Executive_dashboard

def run_test():
    finance = Finance()
    dashboard = Executive_dashboard()
    
    print(finance.execute("refresh_metrics"))
    print(dashboard.execute("refresh_metrics"))

if __name__ == "__main__":
    run_test()
