import asyncio
from launcher_core import A1OSKernel

async def run_tests():
    kernel = A1OSKernel()
    
    # Test 1: Low Risk (Auto-approve)
    intent1 = {"syscall": "deploy", "target": "dev", "requires_approval": True}
    res1 = await kernel.runtime.execute_intent("github_eng", intent1)
    print(f"Test 1 (Low Risk): {res1}")
    
    # Test 2: High Risk (Block)
    intent2 = {"syscall": "deploy", "target": "main", "requires_approval": True}
    res2 = await kernel.runtime.execute_intent("github_eng", intent2)
    print(f"Test 2 (High Risk): {res2}")

if __name__ == "__main__":
    asyncio.run(run_tests())
