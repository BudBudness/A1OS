from control_plane.control_plane import ControlPlane
from pathlib import Path

def run_cbs_attestation():
    root = Path("~/A1OS").expanduser()
    stub_module = root / "generators" / "modules" / "api_gen.py"
    stub_module.parent.mkdir(parents=True, exist_ok=True)
    stub_module.touch(exist_ok=True)
    
    print("🚀 [Attestation] Initializing Capability-Hardened Control Plane...")
    cp = ControlPlane(secret_key="CBS_SECRET_KEY")
    
    # Whitelist the module
    cp.trust.allow("finance_plugin")
    
    # Sign the plugin
    sig = cp.signer.sign("finance_plugin", str(stub_module))
    
    # Register the plugin
    cp.register_trusted_plugin(
        name="finance_plugin",
        module_path=str(stub_module),
        signature_package=sig
    )
    
    # Anchor Capability Manifest: Grant access ONLY to 'market_data' API
    cp.capabilities.register(
        module_name="finance_plugin",
        allowed_apis=["market_data"],
        max_memory_mb=128
    )
    
    # 1. Attestation Test: Authorized API call (Happy Path)
    print("\n✅ [CBS Test 1] Invoking authorized API 'market_data'...")
    try:
        res = cp.execute("finance_plugin", api_endpoint="market_data", payload={"ticker": "A1OS"})
        print(f"  -> Execution accepted: {res.get('status')}")
    except PermissionError as e:
        print(f"❌ [Error] Authorized API incorrectly blocked: {e}")

    # 2. Attestation Test: Unauthorized API call (Adversarial Privilege Escalation)
    print("\n🛑 [CBS Test 2] Simulating privilege escalation (attempting 'trade_exec' API)...")
    try:
        cp.execute("finance_plugin", api_endpoint="trade_exec", payload={"action": "sell"})
        print("❌ [Security Failure] Unauthorized execution bypassed capability boundary!")
    except PermissionError as e:
        print(f"  -> ✔ [Blocked] Privilege escalation securely intercepted: {e}")

if __name__ == "__main__":
    run_cbs_attestation()
