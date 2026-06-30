from control_plane.control_plane import ControlPlane
from pathlib import Path

def run_attestation():
    # Setup paths and environment
    root = Path("~/A1OS").expanduser()
    stub_module = root / "generators" / "modules" / "api_gen.py"
    stub_module.parent.mkdir(parents=True, exist_ok=True)
    stub_module.touch(exist_ok=True)
    
    print("🚀 [Attestation] Initializing secure Control Plane...")
    cp = ControlPlane(secret_key="ATTESTATION_SECRET_KEY")
    
    # 1. Attestation Test: Register an untrusted module
    print("\n📦 [Attestation Test 1] Attempting to register untrusted module...")
    try:
        cp.register_trusted_plugin(
            name="untrusted_api", 
            module_path=str(stub_module), 
            signature_package={"payload": {"hash": "abc"}, "signature": "123"}
        )
    except PermissionError as e:
        print(f"✔ [Blocked] Untrusted registration correctly intercepted: {e}")

    # 2. Attestation Test: Authorize trust, sign payload, and verify registration
    print("\n🔑 [Attestation Test 2] Whitelisting module and generating valid signature...")
    cp.trust.allow("verified_api")
    
    # Sign the actual file using the Control Plane's native signer
    sig = cp.signer.sign("verified_api", str(stub_module))
    
    try:
        cp.register_trusted_plugin(
            name="verified_api",
            module_path=str(stub_module),
            signature_package=sig
        )
        print("✔ [Success] Cryptographically signed plugin successfully ingested!")
    except Exception as e:
        print(f"❌ [Error] Unexpected registration failure: {e}")
        
    # 3. Attestation Test: Invoke execution through compute boundary
    print("\n⚡ [Attestation Test 3] Invoking execution of registered plugin...")
    result = cp.execute("verified_api", payload={"action": "health_check"})
    print(f"✔ [Execution Result] {result}")

if __name__ == "__main__":
    run_attestation()
