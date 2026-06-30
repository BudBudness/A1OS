from api.router import SovereignAPIRouter
from events.core import SovereignEventBus

bus = SovereignEventBus()

@SovereignAPIRouter.register_route("/events/publish", method="POST")
def publish_event(body):
    if not body or "channel" not in body or "message" not in body:
        return 400, {"status": "ERROR", "message": "Missing target channel or message context"}
    frame = bus.dispatch_event(body["channel"], body["message"])
    return 200, {"status": "DISPATCHED", "event_frame": frame}
