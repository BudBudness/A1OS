import os
import sys
import subprocess

ROOT = os.path.expanduser("~/A1OS")
BUILD_SRC = os.path.join(ROOT, "build/src")

def verify_system():
    print("[*] Verification Phase: Auditing generated platform artifacts...")
    errors = 0

    # Global Python Syntax Verification Pass
    print("[*] Running Python syntax check across all emitted modules...")
    for root_dir, _, files in os.walk(BUILD_SRC):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root_dir, file)
                try:
                    subprocess.run([sys.executable, "-m", "py_compile", full_path], check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    print(f"[✘] Syntax Error detected in file: {full_path}\n{e.stderr.decode()}")
                    errors += 1

    if errors == 0:
        print("[✔] Global static syntax validation check passed cleanly.")
    
    print(f"\n[*] VERIFICATION COMPLETE: Status {'[✔] PASSED' if errors == 0 else '[✘] FAILED WITH ERRORS'}")
    sys.exit(0 if errors == 0 else 1)

if __name__ == "__main__":
    verify_system()
