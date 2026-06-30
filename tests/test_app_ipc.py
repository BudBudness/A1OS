import asyncio
from pathlib import Path
from generators.runtime.app_runtime import AppRuntimeEngine

async def main():
    root = Path(__file__).parent.resolve()
    runtime = AppRuntimeEngine(root_dir=str(root), secret_key="FORT_KNOX_KEY")
    
    # 1. Start the Secure IPC Bus
    await runtime.start()
    
    # 2. Write an app module block
    app_module = root / "generators" / "modules" / "secured_app.py"
    app_module.parent.mkdir(parents=True, exist_ok=True)
    app_module.write_text("def run(payload): return True")
    
    # 3. Sign the app package
    sig = runtime.control_plane.signer.sign("secured_app", str(app_module), version=1)
    expected_hash = sig["payload"]["hash"]
    
    # 4. Boot app with strict restricted permissions
    await runtime.boot_app(
        app_id="secured_app",
        module_path=str(app_module),
        signature_package=sig,
        expected_hash=expected_hash,
        allowed_apis=["database_read"] # Explicitly exclude "unauthorized_sys_call"
    )
    
    # 5. Let IPC loops process packets
    await asyncio.sleep(6)
    
    # 6. Tear down system clean
    print("\nShutting down environment...")
    await runtime.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
