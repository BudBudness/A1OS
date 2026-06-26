from pathlib import Path

ROOT = Path.cwd()

FILES = {
"api/server_full.py": "# A1OS API server\n",
"core/kernel.py": "# A1OS kernel\n",
"memory/engine.py": "# Memory engine\n",
"knowledge/engine.py": "# Knowledge engine\n",
"agents/runtime.py": "# Agent runtime\n",
"cluster/manager.py": "# Cluster manager\n",
"consensus/engine.py": "# Consensus engine\n",
"scheduler/engine.py": "# Scheduler engine\n",
"events/bus.py": "# Event bus\n",
"system/status.py": "# System manager\n",
"ui/pwa/index.html": "<!doctype html><html><body><h1>A1OS</h1></body></html>\n",
"ui/pwa/app.js": "// PWA entry\n",
"ui/pwa/app.css": "body{font-family:sans-serif;}\n",
"README.md": "# A1OS v1.0\n",
"requirements.txt": "flask\nflask-cors\n",
}

for rel, content in FILES.items():
p = ROOT / rel
p.parent.mkdir(parents=True, exist_ok=True)
if not p.exists():
p.write_text(content)

(ROOT / "scripts").mkdir(exist_ok=True)
(ROOT / "scripts" / "start.sh").write_text("#!/data/data/com.termux/files/usr/bin/bash\ncd "$(dirname "$0")/.."\npython api/server_full.py\n")

print("A1OS bootstrap complete.")
