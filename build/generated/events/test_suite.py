import asyncio
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