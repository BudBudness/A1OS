class MessengerPlugin:
    def send_alert(self, message):
        # In production, this would be a real API call to Telegram/WhatsApp
        return f"[INTEGRATION] Notification sent: {message}"
