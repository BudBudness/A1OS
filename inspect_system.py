from launcher import A1OSKernel
import asyncio

async def inspect():
    kernel = A1OSKernel()
    print("--- 🔍 SYSTEM DEPENDENCY INSPECTION ---")
    status = {
        "Registry": hasattr(kernel, 'trust_registry'),
        "Signer": hasattr(kernel, 'signer'),
        "ControlPlane": hasattr(kernel, 'control_plane'),
        "Runtime": hasattr(kernel, 'runtime')
    }
    for k, v in status.items():
        print(f"{k}: {'✅ PASS' if v else '❌ FAIL'}")
    
    if all(status.values()):
        print("--- 🏁 INSPECTION COMPLETE: SYSTEM READY ---")
    else:
        print("--- ⚠️ INSPECTION FAILED: SYSTEM INCOMPLETE ---")

if __name__ == "__main__":
    asyncio.run(inspect())
