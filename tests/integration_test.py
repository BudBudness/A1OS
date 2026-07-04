from modules.finance import Finance
from modules.trading import Trading
from modules.executive_dashboard import Executive_dashboard

def run_test():
    finance = Finance()
    trading = Trading()
    dashboard = Executive_dashboard()
    
    print(finance.execute("refresh_metrics"))
    print(trading.execute("poll_market", symbol="BTCUSDT"))
    print(dashboard.execute("refresh_metrics"))

if __name__ == "__main__":
    run_test()
