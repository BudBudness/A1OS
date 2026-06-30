import os
import sys
import json
import time
import shutil
from pathlib import Path
import subprocess
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from generators.runtime_engine import SovereignRuntimeEngine

class ControlLauncher:
    def __init__(self):
        self.specs_dir = PROJECT_ROOT / "queue/specs"
        self.processed_dir = PROJECT_ROOT / "queue/processed"
        self.specs_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def safe_write_json(self, path, data):
        """[ITEM 1] Prevents file truncation via atomic flush and fsync operations."""
        tmp_path = Path(path).with_suffix('.tmp')
        with open(tmp_path, 'w') as f:
            json.dump(data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)

    def compile_framework(self):
        """Runs the generation pipeline."""
        print("\n=== [1/3] EXECUTING FRAMEWORK COMPILATION ===")
        engine = SovereignRuntimeEngine(PROJECT_ROOT)
        engine.run()

    def bounce_server(self):
        """Kills old instances, boots the new build, and executes verification."""
        print("\n=== [2/3] BOUNCING CORE SERVER APPARATUS ===")
        subprocess.run('pkill -f "python3.*server.py"', shell=True, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        
        server_path = PROJECT_ROOT / "build/generated/server.py"
        if not server_path.exists():
            print("❌ Error: build/generated/server.py not found. Compile first.")
            return

        print("🚀 Launching Flask API Server on Port 8086...")
        log_file = open(PROJECT_ROOT / "logs/server.log", "a")
        subprocess.Popen([sys.executable, str(server_path)], stdout=log_file, stderr=log_file)
        
        # [ITEM 3] Autonomous Self-Verification Health Probe Loop
        print("🔬 Running autonomous health verification check...")
        verified = False
        for attempt in range(5):
            time.sleep(1)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8086/health", timeout=1) as response:
                    if response.status == 200:
                        res_body = json.loads(response.read().decode())
                        if res_body.get("status") == "healthy":
                            print(f"✅ Verification Success: Core system validated on attempt {attempt + 1}!")
                            verified = True
                            break
            except Exception:
                pass
                
        if not verified:
            print("❌ Verification Failure: Target server failed health telemetry checks.")

    def poll_queue(self):
        """Continuous loop watching for incoming task specifications."""
        print(f"👀 Sovereign Queue Worker Active. Watching {self.specs_dir} ...")
        try:
            while True:
                spec_files = sorted(list(self.specs_dir.glob("*.json")))
                if spec_files:
                    target_spec = spec_files[0]
                    print(f"\n⚡ Ingesting incoming specification layer: {target_spec.name}")
                    
                    try:
                        spec_data = json.loads(target_spec.read_text())
                        config_path = PROJECT_ROOT / "config/settings.json"
                        current_config = json.loads(config_path.read_text()) if config_path.exists() else {}
                        
                        current_config["active_task"] = spec_data
                        self.safe_write_json(config_path, current_config)
                        
                        self.compile_framework()
                        self.bounce_server()
                        
                        shutil.move(str(target_spec), str(self.processed_dir / target_spec.name))
                        print(f"✅ Task {target_spec.name} processed and cleared successfully.")
                        
                    except Exception as e:
                        print(f"❌ Failed processing job {target_spec.name}: {e}")
                        shutil.move(str(target_spec), str(self.processed_dir / f"FAILED_{target_spec.name}"))
                
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n👋 Queue worker suspended cleanly.")

if __name__ == "__main__":
    launcher = ControlLauncher()
    
    if len(sys.argv) < 2:
        print("Usage: python3 launcher.py [compile | serve | watch]")
        sys.exit(1)
        
    verb = sys.argv[1].lower()
    if verb == "compile":
        launcher.compile_framework()
    elif verb == "serve":
        launcher.bounce_server()
    elif verb == "watch":
        launcher.poll_queue()
    else:
        print(f"Unknown instruction verb: {verb}")
