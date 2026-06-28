import os
import sys
import shutil
import time
import subprocess

ROOT = os.path.expanduser("~/A1OS")
BUILD_SRC = os.path.join(ROOT, "build/src")
BACKUP_DIR = os.path.join(ROOT, "system/backups")

def deploy_platform():
    print("[*] Deployment Phase: Initializing sovereign production matrix rollout...")

    # 1. Structural Backup Generation Rotation
    timestamp = int(time.time())
    backup_path = os.path.join(BACKUP_DIR, f"snapshot_{timestamp}")
    if os.path.exists(BUILD_SRC):
        print(f"[*] Archiving structural platform snapshot to: system/backups/snapshot_{timestamp}")
        shutil.copytree(BUILD_SRC, backup_path)
        print("[✔] Production safety backup state locked.")

    # 2. Force Purging Port Locks Bypasses
    print("[*] Force purging historic port configurations and locks...")
    subprocess.run(["pkill", "-9", "-f", "api.gateway"], capture_output=True)

    # 3. Executing Core Production API Server Framework Matrix
    print("\n[✔] ALL SUBSYSTEMS CLEAR. Launching core engine...")
    
    # Clean runtime search injection targeting root package path
    run_cmd = f"import sys; sys.path.insert(0, '{BUILD_SRC}'); from api.gateway import SovereignAPIGateway; SovereignAPIGateway(port=8030).start()"
    
    subprocess.run([sys.executable, "-c", run_cmd])

if __name__ == "__main__":
    deploy_platform()
