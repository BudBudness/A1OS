class CircuitBreaker:
    def __init__(self, threshold=500.0):
        self.max_spend = threshold
        
    def validate(self, action_type, payload):
        if action_type == "FINANCIAL_PAYOUT" and payload.get("amount", 0) > self.max_spend:
            raise PermissionError("CIRCUIT BREAKER TRIGGERED: Payout exceeds safety limits.")
        return True
