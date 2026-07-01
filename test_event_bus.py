import asyncio
from launcher_core import A1OSKernel

async def notify_ceo(data):
    print(f"🔔 [NOTIFICATION] Alerting CEO: {data.get('message')}")

async def main():
    kernel = A1OSKernel()
    
    # 1. Comm Gateway subscribes to Engineering events
    kernel.bus.subscribe("ENGINEERING_MERGE_SUCCESS", notify_ceo)
    
    # 2. Simulate Engineering triggering the event
    print("🚀 [ENG] Merging PR...")
    await kernel.bus.emit("ENGINEERING_MERGE_SUCCESS", {"message": "PR #402 merged into main."})

if __name__ == "__main__":
    asyncio.run(main())
