def run(payload):
    """
    Tier 3 Empire Finance Risk Engine.
    Emits an internal IPC Intent to save calculations.
    """
    asset = payload.get("asset", "UNKNOWN")
    entry = float(payload.get("entry_price", 0.0))
    current = float(payload.get("current_price", 0.0))
    size = float(payload.get("size", 0.0))
    
    if entry == 0.0:
        return {"status": "ERROR", "message": "Invalid entry parameter"}
        
    pnl = (current - entry) * size
    risk_factor = (pnl / (entry * size)) * 100 if (entry * size) != 0 else 0
    
    # NEW: Formulate a System Call Intent for the Kernel
    intent = {
        "syscall": "database_write",
        "target": "core_database",
        "payload": {
            "action": "write",
            "key": f"market_risk_{asset}",
            "val": f"PNL:{pnl:.2f}|RISK:{risk_factor:.2f}%"
        }
    }
    
    return {
        "status": "CALCULATION_COMPLETE",
        "asset": asset,
        "pnl": pnl,
        "intents": [intent]  # Yield control and data back to the Kernel
    }
