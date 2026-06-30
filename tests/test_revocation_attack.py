from control_plane.control_plane import ControlPlane
from pathlib import Path

def run_revocation_attestation():
    root = Path("~/A1OS").expanduser()
    plugin_module = root / "generators" / "modules" / "revocation_target.py"
    plugin_module.parent.mkdir(parents=True, exist_ok=True)
    plugin_module.write_text("def run(payload): return {'status': 'RUNNING'}")
    
    print("🚀 [Attestation] Initializing Control Plane for Revocation Defense Test...")
    cp = ControlPlane(secret_key="REVOCATION_SECRET_KEY")
    
    # 1. Whitelist, sign, register, and authorize the plugin
    print("\n📝 [Step 1] Registering and enabling 'revocation_plugin'...")
    cp.trust.allow("revocation_plugin")
    sig = cp.signer.sign("revocation_plugin", str(plugin_module))
    
    cp.register_trusted_plugin(
        name="revocation_plugin",
        module_path=str(plugin_module),
        signature_package=sig
    )
    
    # Anchor capability manifest (satisfying the fail-closed policy)
    cp.capabilities.register(
        module_name="revocation_plugin",
        allowed_apis=["system_log"]
    )
    
    # Execute authentic flow (Happy Path)
    print("  -> Invoking pre-revocation execution...")
    res = cp.execute("revocation_plugin", api_endpoint="system_log")
    print(f"     Execution result: {res.get('status')}")

    # 2. Adversarial Action / Administrative Revocation
    print("\n🪝 [Step 2] SIMULATING REVOCATION: Revoking trust from 'revocation_plugin'...")
    cp.trust.revoke("revocation_plugin")
    
    # Attempt execution post-revocation
    print("\n🚨 [Step 3] Executing revoked plugin expecting hard denial...")
    try:
        cp.execute("revocation_plugin", api_endpoint="system_log")
        print("❌ [Security Failure] Revoked plugin successfully bypassed execution gate!")
    except PermissionError as e:
        print(f"  -> ✔ [Blocked] Revocation successfully halted execution: {e}")

if __name__ == "__main__":
    run_revocation_attestation()
