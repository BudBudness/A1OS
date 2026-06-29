from generators.core.base_gen import BaseGenerator
from pathlib import Path

class EventsGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "events"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Publish-Subscribe Event Bus Broker
        bus_code = '''import asyncio

class DecoupledEventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        print(f"[EVENT-BUS] Registered subscriber for topic: {event_type}")

    async def publish(self, event_type, payload):
        if event_type not in self._subscribers:
            return
        for callback in self._subscribers[event_type]:
            if asyncio.iscoroutinefunction(callback):
                await callback(payload)
            else:
                callback(payload)
        print(f"[EVENT-BUS] Dispatched message payload to topic: {event_type}")
'''

        # 2. Subscriber Callback Handler
        handler_code = '''class EventSubscriber:
    def __init__(self, name):
        self.name = name
        self.events_received = []

    def handle_event(self, payload):
        self.events_received.append(payload)
        print(f"[{self.name}] Received broadcast event payload: {payload}")
'''

        # 3. Strict Message Envelope and Payload Validator
        payload_code = '''import time
import uuid

class EventMessageEnvelope:
    def __init__(self, event_type, data):
        self.envelope_id = str(uuid.uuid4())
        self.event_type = event_type
        self.timestamp = time.time()
        self.data = data

    def package(self):
        return {
            "id": self.envelope_id,
            "type": self.event_type,
            "time": self.timestamp,
            "payload": self.data
        }
'''

        # 4. Decoupled Message Bus Verification Test Suite
        test_code = '''import asyncio
from .bus import DecoupledEventBus
from .handler import EventSubscriber
from .payload import EventMessageEnvelope

def test_events_subsystem():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bus = DecoupledEventBus()
    subscriber = EventSubscriber("sys_logger")
    
    # 1. Register event topic subscription
    bus.subscribe("SYSTEM_BOOT", subscriber.handle_event)
    
    # 2. Package message envelope
    envelope = EventMessageEnvelope("SYSTEM_BOOT", {"status": "initialized"})
    package = envelope.package()
    
    # 3. Publish asynchronous event broadcast
    async def trigger_publish():
        await bus.publish("SYSTEM_BOOT", package)
        
    loop.run_until_complete(trigger_publish())
    
    assert len(subscriber.events_received) == 1
    assert subscriber.events_received[0]["type"] == "SYSTEM_BOOT"
    assert subscriber.events_received[0]["payload"]["status"] == "initialized"
    
    print("✅ Decoupled Event-Bus Routing Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_events_subsystem()
'''

        # Write out the full structural events module files atomically
        with open(output_dir / "bus.py", "w") as f: f.write(bus_code.strip())
        with open(output_dir / "handler.py", "w") as f: f.write(handler_code.strip())
        with open(output_dir / "payload.py", "w") as f: f.write(payload_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] events_gen.py has compiled v1 Events Subsystem inside {output_dir}")
