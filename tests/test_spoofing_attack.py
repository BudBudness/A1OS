from control_plane.control_plane import ControlPlane
from pathlib import Path

def run_spoofing_attestation():
    root = Path("~/A1OS").expanduser()
    
    # Legitimate setup
    legit_module = root / "generators" / "modules" / "legitimate_service.py"
    legit_module.parent.mkdir(parents=True, exist_ok=True)
    legit_module.write_text("def run(payload): return {'status': 'LEGITIMATE_RUN'}")
    
    # Rogue setup (Attacker attempts to use the same logical name)
    rogue_module = root / "generators" / "modules" / "rogue_service.py"
    rogue_module.write_text("def run(payload): return {'status': 'MALICIOUS_TAKEOVER'}")
    
    print("🚀 [Attestation] Initializing Control Plane for Name Spoofing Defense Test...")
    cp = ControlPlane(secret_key="SPOOF_SECRET_KEY")
    
    # 1. Register and anchor the legitimate plugin
    print("\n📝 [Step 1] Registering legitimate module 'core_finance'...")
    cp.trust.allow("core_finance")
    sig_legit = cp.signer.sign("core_finance", str(legit_module))
    
    cp.register_trusted_plugin(
        name="core_finance",
        module_path=str(legit_module),
        signature_package=sig_legit
    )
    
    # Execute authentic flow (Happy Path)
    res = cp.execute("core_finance", api_endpoint="system_log")
    print(f"   Legitimate execution result: {res.get('status')}")

    # 2. Adversarial Action: Attempt to register a rogue file under the exact same trusted name "core_finance"
    print("\n🪪 [Step 2] SIMULATING SPOOFING ATTACK: Registering rogue file under trusted name...")
    
    # The attacker signs the malicious file using the compromised/known key, claiming it is "core_finance"
    sig_rogue = cp.signer.sign("core_finance", str(rogue_module))
    
    try:
        # The registry should ideally reject this overwrite if it's already bound to a distinct path,
        # or verify that the signature package fundamentally conflicts with the established state.
        cp.register_trusted_plugin(
            name="core_finance",
            module_path=str(rogue_module),
            signature_package=sig_rogue
        )
        print("❌ [Security Failure] Registry allowed name-squatting over an existing trusted plugin!")
        
        # Test execution to see if the rogue module overrides the legit one
        res_rogue = cp.execute("core_finance", api_endpoint="system_log")
        print(f"   ⚠️ Compromised execution result: {res_rogue.get('status')}")
        
    except (PermissionError, ValueError) as e:
        print(f"  -> ✔ [Blocked] Name spoofing/replacement attempt securely intercepted: {e}")

if __name__ == "__main__":
    run_spoofing_attestation()
