#!/usr/bin/env python3
import os, sys, subprocess, time, json, shutil
from pathlib import Path
from datetime import datetime

class Orchestrator:
    def __init__(self):
        self.root = Path.cwd()
        self.milestone = 0
        self.port = 8086  # Production port
        self.backup_dir = self.root / "backups" / "deploy"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.status = {"steps": [], "errors": [], "timestamp": datetime.now().isoformat()}

    def log(self, msg, status="INFO"):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {status}: {msg}")
        self.status["steps"].append({"msg": msg, "status": status, "time": datetime.now().isoformat()})

    def execute(self, cmd, cwd=None, check=True):
        """Command executor (renamed to avoid collision)"""
        self.log(f"Executing: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd or self.root, capture_output=True, text=True)
        if result.returncode != 0:
            self.log(f"Failed: {result.stderr}", "ERROR")
            if check:
                self.status["errors"].append(result.stderr)
                return False
        if result.stdout and result.stdout.strip():
            self.log(result.stdout.strip(), "OUTPUT")
        return True

    def bootstrap(self):
        self.log("Phase 1: Bootstrap")
        return self.execute("python3 bootstrap.py")

    def generate(self):
        self.log("Phase 2: Generate")
        return self.execute("python3 generate.py")

    def verify(self):
        self.log("Phase 3: Verify")
        return self.execute("python3 verify.py")

    def backup(self):
        self.log("Phase 4: Backup")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"pre_deploy_{ts}"
        if (self.root / "build/generated").exists():
            shutil.copytree(self.root / "build/generated", backup_path, dirs_exist_ok=True)
            self.log(f"✅ Backup saved to {backup_path}")
        return True

    def deploy(self):
        self.log("Phase 5: Deploy")
        # Kill existing processes on production port
        self.execute(f"pkill -f 'gunicorn.*:{self.port}' 2>/dev/null || true", check=False)
        self.execute(f"fuser -k {self.port}/tcp 2>/dev/null || true", check=False)
        # Start production server (use generated server, not phase1)
        server_path = self.root / "build/generated/server.py"
        if not server_path.exists():
            self.log("No server.py found, using phase1_api.py", "WARNING")
            server_path = self.root / "build/generated/phase1_api.py"
        return self.execute(f"python3 {server_path} > logs/server.log 2>&1 &")

    def health_check(self):
        self.log("Phase 6: Health Check")
        time.sleep(3)
        endpoints = ["/", "/health", "/routes", "/system/status"]
        for endpoint in endpoints:
            result = subprocess.run(
                f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{self.port}{endpoint}",
                shell=True, capture_output=True, text=True
            )
            if result.stdout == "200":
                self.log(f"✅ {endpoint} OK", "OK")
            else:
                self.log(f"❌ {endpoint} failed (HTTP {result.stdout})", "ERROR")
                return False
        return True

    def run_tests(self):
        self.log("Phase 7: Run Tests")
        if (self.root / "tests").exists():
            result = subprocess.run("python3 -m pytest tests/", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ All tests passed", "OK")
                return True
            else:
                self.log(f"❌ Tests failed: {result.stdout}", "ERROR")
                return False
        else:
            self.log("No tests found, skipping", "WARNING")
            return True

    def rollback(self):
        self.log("Phase 8: Rollback")
        backups = sorted(self.backup_dir.glob("pre_deploy_*"), reverse=True)
        if backups:
            latest = backups[0]
            self.log(f"Restoring from {latest}")
            shutil.rmtree(self.root / "build/generated", ignore_errors=True)
            shutil.copytree(latest, self.root / "build/generated", dirs_exist_ok=True)
            self.log("✅ Rollback complete")
            return self.deploy()
        self.log("No backup found, rollback skipped", "WARNING")
        return True

    def commit(self):
        self.log("Phase 9: Commit")
        self.execute("git add -A", check=False)
        result = subprocess.run("git diff --cached --quiet", shell=True)
        if result.returncode == 0:
            self.log("No changes to commit", "WARNING")
            return True
        return self.execute('git commit -m "Orchestrator milestone: auto-generated" --no-verify')

    def next_milestone(self):
        self.milestone += 1
        self.log(f"Phase 10: Next Milestone ({self.milestone})")
        return True

    def run(self):
        self.log("=== A1OS ORCHESTRATOR STARTED ===")
        phases = [
            self.bootstrap,
            self.generate,
            self.verify,
            self.backup,
            self.deploy,
            self.health_check,
            self.run_tests,
            self.commit,
            self.next_milestone
        ]
        for phase in phases:
            if not phase():
                self.log("Orchestrator halted — initiating rollback", "ERROR")
                self.rollback()
                return False
        self.log("=== ORCHESTRATOR COMPLETE ===")
        return True

if __name__ == "__main__":
    orch = Orchestrator()
    orch.run()
