def run(payload):
    """
    Tier 2 Communication Gateway (WhatsApp/Telegram Webhook Target).
    Payload format: {"source": "whatsapp"|"telegram", "message": str}
    """
    source = payload.get("source", "unknown")
    message = payload.get("message", "")
    
    print(f"📲 Inbound communication packet intercepted from [{source.upper()}]: {message}")
    
    # Securely simulate processing or notification triggers
    return {
        "status": "PROCESSED",
        "gateway": source,
        "payload_digest": hash(message)
    }
