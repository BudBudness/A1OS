class SovereignEventBus:
    def __init__(self):
        self.history = []
    def dispatch_event(self, channel, message):
        event_frame = {"channel": channel, "payload": message, "index": len(self.history)}
        self.history.append(event_frame)
        return event_frame
