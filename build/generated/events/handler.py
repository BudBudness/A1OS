class EventSubscriber:
    def __init__(self, name):
        self.name = name
        self.events_received = []

    def handle_event(self, payload):
        self.events_received.append(payload)
        print(f"[{self.name}] Received broadcast event payload: {payload}")