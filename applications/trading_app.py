from applications.framework.base_app import BaseApp

class TradingApp(BaseApp):
    def run_strategy(self, strategy_name):
        # Compose multiple actions across departments
        # 1. Budget check via CFO
        result_1 = self.execute("Finance", f"Allocate funds for {strategy_name}")
        # 2. Infrastructure deployment via CTO
        result_2 = self.execute("Engineering", f"Initialize trading bot for {strategy_name}")
        
        return f"{self.name} Status: {result_1} | {result_2}"
