import os
from pathlib import Path

ROOT = Path.cwd()

files = {
    "api/server_full.py": '''
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
from datetime import datetime
from memory.store import MemoryStore
from system.health import HealthCheck

app = Flask(__name__)
CORS(app)

memory = MemoryStore()
health = HealthCheck()

@app.route("/")
def root():
    return jsonify({"status": "online", "version": "A1OS v1.0", "modules": ["memory"]})

@app.route("/memory", methods=["GET", "POST"])
def memory_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text"}), 400
        result = memory.add(data["text"])
        return jsonify({"ok": True, "id": result["id"]})
    return jsonify(memory.get_all())

@app.route("/health")
def health_check():
    return jsonify(health.check())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
''',

    "memory/store.py": '''
import hashlib
from datetime import datetime

class MemoryStore:
    def __init__(self):
        self.store = {}

    def add(self, text):
        doc_id = hashlib.md5(text.encode()).hexdigest()
        self.store[doc_id] = {"id": doc_id, "text": text, "created": datetime.now().isoformat()}
        return self.store[doc_id]

    def get_all(self):
        return list(self.store.values())

    def search(self, query):
        q = query.lower()
        return [m for m in self.store.values() if q in m["text"].lower()]
''',

    "system/health.py": '''
from datetime import datetime

class HealthCheck:
    def check(self):
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
''',

    "config/settings.py": '''
import os

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
API_PORT = int(os.getenv("API_PORT", 8086))
PWA_PORT = int(os.getenv("PWA_PORT", 8000))
''',

    "scripts/start.sh": '''#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p logs
echo "🚀 Starting A1OS..."
pkill -f "python3 api/server_full.py" 2>/dev/null
nohup python3 api/server_full.py > logs/server.log 2>&1 &
sleep 2
echo "✅ Backend: http://localhost:8086"
curl -s http://localhost:8086/ | python3 -m json.tool
''',

    "requirements.txt": '''
flask
flask-cors
''',

    "tests/test_api.py": '''
import requests
import json

def test_root():
    r = requests.get("http://localhost:8086/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"

def test_memory():
    r = requests.post("http://localhost:8086/memory", json={"text": "test"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] == True

def test_health():
    r = requests.get("http://localhost:8086/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

if __name__ == "__main__":
    test_root()
    test_memory()
    test_health()
    print("✅ All tests passed!")
'''
}

for path, content in files.items():
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip())

for script in ROOT.glob("scripts/*.sh"):
    script.chmod(0o755)

print("✅ Source files generated")
