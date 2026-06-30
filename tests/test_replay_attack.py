from control_plane.control_plane import ControlPlane
from pathlib import Path

def run_replay_attestation():
    root = Path("~/A1OS").expanduser()
    module_path = root / "generators" / "modules" / "replay_target.py"
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("def run(payload): return {'status': 'OK'}")
    
    cp = ControlPlane(secret_key="SUPER_SECRET_KEY")
    
    # 1. Successful registration of Version 1
    print("🚀 [Step 1] Registering Version 1...")
    sig_v1 = cp.signer.sign("my_plugin", str(module_path), version=1)
    cp.register_trusted_plugin("my_plugin", str(module_path), sig_v1)
    print("   -> Success: Version 1 anchored.")

    # 2. Replay/Rollback Attack: Attempt to register Version 1 again
    print("\n⚠️ [Step 2] Attacker attempting Replay (v1 -> v1)...")
    try:
        # Re-signing with the same version
        sig_v1_replay = cp.signer.sign("my_plugin", str(module_path), version=1)
        cp.register_trusted_plugin("my_plugin", str(module_path), sig_v1_replay)
        print("❌ [Security Failure] Replay attack accepted!")
    except ValueError as e:
        print(f"   -> ✔ [Blocked] Replay attempt rejected: {e}")

    # 3. Rollback Attack: Attempt to register Version 0 (downgrade)
    print("\n⚠️ [Step 3] Attacker attempting Rollback (v1 -> v0)...")
    try:
        sig_v0 = cp.signer.sign("my_plugin", str(module_path), version=0)
        cp.register_trusted_plugin("my_plugin", str(module_path), sig_v0)
        print("❌ [Security Failure] Rollback attack accepted!")
    except ValueError as e:
        print(f"   -> ✔ [Blocked] Rollback attempt rejected: {e}")

if __name__ == "__main__":
    run_replay_attestation()
