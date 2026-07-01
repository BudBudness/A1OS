import os
from generators.core.base_gen import BaseGenerator

class Generator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)
        self.name = "events"
        self.dependencies = ["api"]

    def generate(self):
        artifacts = []
        core_src = """class SovereignEventBus:
    def __init__(self):
        self.history = []
    def dispatch_event(self, channel, message):
        event_frame = {"channel": channel, "payload": message, "index": len(self.history)}
        self.history.append(event_frame)
        return event_frame
"""
        routes_src = """from api.router import SovereignAPIRouter
from events.core import SovereignEventBus

bus = SovereignEventBus()

@SovereignAPIRouter.register_route("/events/publish", method="POST")
def publish_event(body):
    if not body or "channel" not in body or "message" not in body:
        return 400, {"status": "ERROR", "message": "Missing target channel or message context"}
    frame = bus.dispatch_event(body["channel"], body["message"])
    return 200, {"status": "DISPATCHED", "event_frame": frame}
"""
        artifacts.append(self.emit_file("events", "core.py", core_src))
        artifacts.append(self.emit_file("events", "events_routes.py", routes_src))
        return artifacts
