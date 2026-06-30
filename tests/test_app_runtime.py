import asyncio
from pathlib import Path
from generators.runtime.app_runtime import AppRuntimeEngine

async def main():
    root = Path(__file__).parent.resolve()
    
    # 1. Initialize our async runtime engine
    runtime = AppRuntimeEngine(root_dir=str(root), secret_key="FORT_KNOX_KEY")
    
    # 2. Setup a dummy application file on disk
    app_module = root / "generators" / "modules" / "user_app.py"
    app_module.parent.mkdir(parents=True, exist_ok=True)
    app_module.write_text("def run(payload): return {'status': 'APP_ACTIVE'}")
    
    print("💎 [Step 1] Creating cryptographic signature package for the app...")
    sig = runtime.control_plane.signer.sign("user_app", str(app_module), version=1)
    expected_hash = sig["payload"]["hash"]
    
    # 3. Securely boot the application inside the worker pool
    print("\n🚀 [Step 2] Passing app package to the Runtime Engine...")
    await runtime.boot_app(
        app_id="user_app",
        module_path=str(app_module),
        signature_package=sig,
        expected_hash=expected_hash,
        allowed_apis=["database_read", "network_post"]
    )
    
    # 4. Let the app run for a couple of cycles
    print("\n⏳ [Step 3] Monitoring active background process worker (2 cycles)...")
    await asyncio.sleep(6)
    
    print(f"Current app state in pool: {runtime.active_apps.get('user_app', {}).get('status')}")
    
    # 5. Gracefully terminate and evict the app
    print("\n🧹 [Step 4] Triggering hot-eviction from runtime environment...")
    await runtime.terminate_app("user_app")
    
    print("\n✅ Verification complete.")

if __name__ == "__main__":
    asyncio.run(main())
