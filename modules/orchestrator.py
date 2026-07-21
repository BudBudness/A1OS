from modules.trading import Trading
from modules.procurement import Procurement

class Orchestrator:
    def __init__(self):
        self.trading = Trading()
        self.procurement = Procurement()

    def run_cycle(self, trade_side, trade_symbol, supply_item, supply_qty):
        # 1. Execute trade
        trade_result = self.trading.execute("execute_trade", side=trade_side, symbol=trade_symbol)
        
        # 2. Logic gate: Only procure if trade is successful
        # Assuming "Success" is part of the string returned by Trading module
        if "Success" in trade_result:
            procure_result = self.procurement.execute("order_supplies", item=supply_item, quantity=supply_qty)
            return f"Trade Result: {trade_result} | Procurement Result: {procure_result}"
        else:
            return f"Trade Failed: {trade_result} | Procurement Aborted"

if __name__ == "__main__":
    orch = Orchestrator()
    print(orch.run_cycle("BUY", "BTCUSDT", "Artificial Grass", 50))
