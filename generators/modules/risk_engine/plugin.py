def run(payload):
    """
    Tier 3 Empire Finance Risk Management Engine.
    Payload format: {"asset": str, "entry_price": float, "current_price": float, "size": float}
    """
    asset = payload.get("asset", "UNKNOWN")
    entry = float(payload.get("entry_price", 0.0))
    current = float(payload.get("current_price", 0.0))
    size = float(payload.get("size", 0.0))
    
    if entry == 0.0:
        return {"status": "ERROR", "message": "Invalid entry parameter baseline."}
        
    pnl = (current - entry) * size
    risk_factor = (pnl / (entry * size)) * 100 if (entry * size) != 0 else 0
    
    print(f"📈 Analytics execution for [{asset}] -> Real-time PnL: {pnl:.2f} | Risk Variance: {risk_factor:.2f}%")
    
    return {
        "status": "CALCULATION_COMPLETE",
        "asset": asset,
        "pnl": pnl,
        "risk_variance_pct": round(risk_factor, 2)
    }
