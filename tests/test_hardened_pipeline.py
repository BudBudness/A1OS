from control_plane.control_plane import ControlPlane
from pathlib import Path

def run_hardened_pipeline_test():
    root = Path("~/A1OS").expanduser()
    main_module = root / "generators" / "modules" / "main_service.py"
    main_module.parent.mkdir(parents=True, exist_ok=True)
    
    # Write legitimate plugin code
    main_module.write_text("def run(payload): return {'status': 'SECURE_RUN'}")
    
    cp = ControlPlane(secret_key="FORT_KNOX_KEY")
    
    print("🚀 [Step 1] Registering plugin with secured dependencies...")
    cp.trust.allow("secure_service")
    
    # Sign the plugin (obtaining its valid hash)
    sig = cp.signer.sign("secure_service", str(main_module), version=1)
    expected_hash = sig["payload"]["hash"]
    
    cp.register_trusted_plugin("secure_service", str(main_module), sig)
    
    # Anchor capabilities & explicit dependencies
    cp.capabilities.register(
        module_name="secure_service", 
        allowed_apis=["system_log"], 
        required_dependencies=["crypto_helper", "network_utils"]
    )
    
    # 2. Happy Path Execution (Pre-flight passes)
    print("\n📦 [Step 2] Executing verified state...")
    res = cp.runner.run(str(main_module), expected_hash, payload={"cmd": "init"})
    print(f"   -> Execution Result: {res.get('status')}")

    # 3. TOCTOU Attack: Attacker swaps file contents during the race condition window
    print("\n🔪 [Step 3] Simulating TOCTOU attack (Swapping file contents right before execution)...")
    # Attacker overwrites the file bytes on disk without changing the path
    main_module.write_text("def run(payload): return {'status': 'MALICIOUS_TAKEOVER'}")
    
    try:
        # Runner uses expected hash; pre-flight calculation fails-closed
        cp.runner.run(str(main_module), expected_hash, payload={"cmd": "init"})
        print("❌ [Security Failure] TOCTOU swap bypassed pre-flight integrity check!")
    except PermissionError as e:
        print(f"   -> ✔ [Blocked] TOCTOU attempt intercepted by pre-flight check: {e}")

if __name__ == "__main__":
    run_hardened_pipeline_test()
