from modules.trading import Trading
from modules.procurement import Procurement

class Orchestrator:
    def __init__(self):
        self.trading = Trading()
        self.procurement = Procurement()

    def run_cycle(self, trade_side, trade_symbol, supply_item, supply_qty):
        # Execute trade
        trade_result = self.trading.execute("execute_trade", side=trade_side, symbol=trade_symbol)
        # Trigger procurement if trade successful
        procure_result = self.procurement.execute("order_supplies", item=supply_item, quantity=supply_qty)
        return f"{trade_result} | {procure_result}"

if __name__ == "__main__":
    orch = Orchestrator()
    print(orch.run_cycle("BUY", "BTCUSDT", "Artificial Grass", 50))
