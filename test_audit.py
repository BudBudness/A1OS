import asyncio
from launcher_core import A1OSKernel

async def audit_logger(data):
    print(f"🔍 [AUDIT LOG] App: {data['app']} | Action: {data['action']}")

async def main():
    kernel = A1OSKernel()
    kernel.bus.subscribe("GOVERNANCE_AUDIT", audit_logger)
    
    print("🚀 [ENG] Sending intent...")
    await kernel.runtime.execute_intent("github_eng", {"syscall": "deploy_prod", "requires_approval": False})

if __name__ == "__main__":
    asyncio.run(main())
